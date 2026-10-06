from typing import cast

import questionary
import typer
from rich.table import Table

from phd_artifacts.artifacts import PushAction, RemoteArtifactConflictError
from phd_artifacts.artifacts.models import Artifact
from phd_artifacts.artifacts.queries import get_artifacts
from phd_artifacts.artifacts.status import (
    ArtifactRemoteState,
    get_artifact_remote_states,
)
from phd_artifacts.artifacts.transfer import (
    PushResult,
    finalize_push,
    perform_push_transfer,
    prepare_push,
)
from phd_artifacts.cli.artifacts.common import resolve_artifact_or_exit
from phd_artifacts.cli.remotes.common import resolve_remote_name
from phd_artifacts.cli.ui import activity, checkbox, confirm, console
from phd_artifacts.remotes.backends.exceptions import UnsupportedBackendError
from phd_artifacts.remotes.exceptions import RemoteNotFoundError


def _push_artifact(
    artifact: Artifact,
    remote_name: str,
    force: bool,
) -> PushResult:
    """Push a promoted artifact to a configured remote."""

    def prepare(force_value: bool):
        with activity("Preparing upload") as reporter:
            return prepare_push(
                artifact=artifact,
                remote_name=remote_name,
                force=force_value,
                progress=reporter,
            )

    try:
        try:
            prepared = prepare(force)

        except RemoteArtifactConflictError:
            if not confirm(
                f"Remote artifact '{artifact.name}' differs. Overwrite remote copy?",
                default=False,
            ):
                raise typer.Exit(0) from None

            prepared = prepare(True)

        # rclone owns the terminal here
        result = perform_push_transfer(prepared)

        # Our spinner resumes after the transfer
        with activity("Updating remote index"):
            finalize_push(prepared)

        return result

    except (
        RemoteNotFoundError,
        UnsupportedBackendError,
        ValueError,
        RuntimeError,
        FileNotFoundError,
    ) as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None


def _render_push_result(
    artifact: Artifact,
    remote_name: str,
    result: PushResult,
) -> None:
    match result.action:
        case PushAction.UPLOADED:
            console.print(f"\n[success]Artifact '{artifact.name}' uploaded successfully.[/success]")

        case PushAction.ALREADY_UP_TO_DATE:
            console.print(f"\n[success]Artifact '{artifact.name}' is already up to date.[/success]")

        case PushAction.OVERWRITTEN:
            console.print(
                f"\n[warning]Artifact '{artifact.name}' overwritten successfully.[/warning]"
            )

    console.print(f"Remote:      {remote_name}")
    console.print(f"Destination: {result.destination}")


def _render_push_results(
    results: list[tuple[Artifact, PushResult]],
    remote_name: str,
) -> None:
    table = Table(
        "Artifact",
        "Version",
        "Action",
    )

    for artifact, result in results:
        match result.action:
            case PushAction.UPLOADED:
                action = "[success]uploaded[/success]"

            case PushAction.ALREADY_UP_TO_DATE:
                action = "[success]up to date[/success]"

            case PushAction.OVERWRITTEN:
                action = "[warning]overwritten[/warning]"

        table.add_row(
            artifact.name,
            artifact.version,
            action,
        )

    console.print()
    console.print(table)
    console.print(f"Remote: {remote_name}")


def push(
    name: str | None = typer.Argument(
        None,
        help="Artifact name. Omit to select pending artifacts.",
    ),
    remote: str | None = typer.Option(
        None,
        "--remote",
        "-r",
        help="Destination remote.",
    ),
    version: str | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Artifact version.",
    ),
    project: str | None = typer.Option(
        None,
        "--project",
        "-p",
        help="Project name.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite remote artifacts if they differ.",
    ),
    all_: bool = typer.Option(
        False,
        "--all",
        help="Push all pending artifacts without selection.",
    ),
):
    """Push promoted artifacts to remote storage."""

    if name is not None and all_:
        raise typer.BadParameter("--all cannot be used together with an artifact name.")

    if name is None and version is not None:
        raise typer.BadParameter("--version requires an artifact name.")

    remote_name = resolve_remote_name(remote)

    #
    # Single artifact
    #
    if name is not None:
        artifact = resolve_artifact_or_exit(
            console=console,
            name=name,
            version=version,
            project=project,
        )

        result = _push_artifact(
            artifact=artifact,
            remote_name=remote_name,
            force=force,
        )

        _render_push_result(
            artifact=artifact,
            remote_name=remote_name,
            result=result,
        )

        return

    #
    # Multiple artifacts
    #
    artifacts = get_artifacts(
        project=project,
    )

    if not artifacts:
        console.print("[warning]No local artifacts found.[/warning]")
        raise typer.Exit(0)

    try:
        with activity(f"Checking artifacts against '{remote_name}'") as reporter:
            states = get_artifact_remote_states(
                artifacts=artifacts,
                remote_name=remote_name,
                progress=reporter,
            )

    except (
        RemoteNotFoundError,
        UnsupportedBackendError,
        ValueError,
        RuntimeError,
        FileNotFoundError,
    ) as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None

    pending = [state for state in states if state.pending]

    if not pending:
        console.print(f"[success]All artifacts are up to date on '{remote_name}'.[/success]")
        raise typer.Exit(0)

    if all_:
        selected_states = pending

    else:
        selected = checkbox(
            "Select artifacts to push:",
            [
                questionary.Choice(
                    title=(f"{state.artifact.name} [{state.status.value.replace('_', ' ')}]"),
                    value=state,
                )
                for state in pending
            ],
        )

        selected_states = [cast(ArtifactRemoteState, item) for item in selected]

    results: list[tuple[Artifact, PushResult]] = []

    for state in selected_states:
        result = _push_artifact(
            artifact=state.artifact,
            remote_name=remote_name,
            force=force,
        )

        results.append(
            (
                state.artifact,
                result,
            )
        )

    _render_push_results(
        results=results,
        remote_name=remote_name,
    )
