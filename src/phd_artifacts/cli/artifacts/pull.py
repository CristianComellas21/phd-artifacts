from typing import cast

import questionary
import typer
from rich.table import Table

from phd_artifacts.artifacts.exceptions import LocalArtifactConflictError
from phd_artifacts.artifacts.models import RemoteArtifact
from phd_artifacts.artifacts.queries import get_remote_artifacts
from phd_artifacts.artifacts.status import (
    RemoteArtifactLocalState,
    get_remote_artifact_local_states,
)
from phd_artifacts.artifacts.transfer import (
    PullAction,
    PullResult,
    perform_pull,
    prepare_pull,
    verify_pulled_artifact,
)
from phd_artifacts.cli.artifacts.common import resolve_remote_artifact_or_exit
from phd_artifacts.cli.remotes.common import resolve_remote_name
from phd_artifacts.cli.ui import (
    activity,
    checkbox,
    confirm,
    console,
)
from phd_artifacts.remotes.exceptions import RemoteError


def _pull_artifact(
    artifact: RemoteArtifact,
    force: bool,
) -> PullResult:
    """Pull a promoted artifact from a configured remote."""

    def prepare(force_value: bool):
        with activity("Preparing download") as reporter:
            return prepare_pull(
                artifact=artifact,
                force=force_value,
                progress=reporter,
            )

    try:
        try:
            prepared = prepare(force)

        except LocalArtifactConflictError:
            if not confirm(
                f"Local artifact '{artifact.name}' differs. Overwrite local copy?",
                default=False,
            ):
                raise typer.Exit(0) from None

            prepared = prepare(True)

        result = perform_pull(prepared)

        if result.action is not PullAction.ALREADY_UP_TO_DATE:
            with activity("Verifying download") as reporter:
                verify_pulled_artifact(
                    prepared,
                    progress=reporter,
                )

        return result

    except (RemoteError, RuntimeError, FileNotFoundError, ValueError) as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None


def _render_pull_result(
    artifact: RemoteArtifact,
    result: PullResult,
) -> None:
    match result.action:
        case PullAction.ALREADY_UP_TO_DATE:
            console.print("[success]Artifact is already up to date.[/success]")

        case PullAction.OVERWRITTEN:
            console.print("[warning]Artifact overwritten from remote.[/warning]")

        case PullAction.DOWNLOADED:
            console.print("[success]Artifact downloaded successfully.[/success]")

    console.print(f"Remote:   {artifact.remote}")
    console.print(f"Artifact: {artifact.name}")
    console.print(f"Version:  {artifact.version}")
    console.print(f"Path:     {result.destination}")


def _render_pull_results(
    results: list[tuple[RemoteArtifact, PullResult]],
    remote_name: str,
) -> None:
    table = Table(
        "Artifact",
        "Version",
        "Action",
    )

    for artifact, result in results:
        match result.action:
            case PullAction.DOWNLOADED:
                action = "[success]downloaded[/success]"

            case PullAction.ALREADY_UP_TO_DATE:
                action = "[success]up to date[/success]"

            case PullAction.OVERWRITTEN:
                action = "[warning]overwritten[/warning]"

        table.add_row(
            artifact.name,
            artifact.version,
            action,
        )

    console.print()
    console.print(table)
    console.print(f"Remote: {remote_name}")


def pull(
    name: str | None = typer.Argument(
        None,
        help="Artifact name. Omit to select pending artifacts.",
    ),
    remote: str | None = typer.Option(
        None,
        "--remote",
        "-r",
        help="Remote name.",
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
        help="Overwrite different local artifacts.",
    ),
    all_: bool = typer.Option(
        False,
        "--all",
        help="Pull all pending artifacts without selection.",
    ),
):
    """Pull promoted artifacts from a configured remote."""

    if name is not None and all_:
        raise typer.BadParameter("--all cannot be used together with an artifact name.")

    if name is None and version is not None:
        raise typer.BadParameter("--version requires an artifact name.")

    remote_name = resolve_remote_name(remote)

    #
    # Single artifact
    #
    if name is not None:
        artifact = resolve_remote_artifact_or_exit(
            console=console,
            remote_name=remote_name,
            name=name,
            project=project,
            version=version,
        )

        result = _pull_artifact(
            artifact=artifact,
            force=force,
        )

        _render_pull_result(
            artifact=artifact,
            result=result,
        )

        return

    #
    # Multiple artifacts
    #
    try:
        with activity(f"Reading artifacts from '{remote_name}'"):
            artifacts = get_remote_artifacts(
                remote_name=remote_name,
                project=project,
            )

        if not artifacts:
            console.print(f"[warning]No artifacts found on '{remote_name}'.[/warning]")
            raise typer.Exit(0)

        with activity("Comparing remote artifacts with local store") as reporter:
            states = get_remote_artifact_local_states(
                artifacts=artifacts,
                progress=reporter,
            )

    except (RemoteError, RuntimeError, FileNotFoundError, ValueError) as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None

    pending = [state for state in states if state.pending]

    if not pending:
        console.print(
            f"[success]All artifacts from '{remote_name}' are up to date locally.[/success]"
        )
        raise typer.Exit(0)

    if all_:
        selected_states = pending

    else:
        selected = checkbox(
            "Select artifacts to pull:",
            [
                questionary.Choice(
                    title=(f"{state.artifact.name} [{state.status.value.replace('_', ' ')}]"),
                    value=state,
                )
                for state in pending
            ],
        )

        selected_states = [cast(RemoteArtifactLocalState, item) for item in selected]

    results: list[tuple[RemoteArtifact, PullResult]] = []

    for state in selected_states:
        result = _pull_artifact(
            artifact=state.artifact,
            force=force,
        )

        results.append(
            (
                state.artifact,
                result,
            )
        )

    _render_pull_results(
        results=results,
        remote_name=remote_name,
    )
