import typer

from phd_artifacts.artifacts import PushAction, RemoteArtifactConflictError
from phd_artifacts.artifacts.models import Artifact
from phd_artifacts.artifacts.transfer import (
    PushResult,
    perform_push,
    prepare_push,
)
from phd_artifacts.cli.artifacts.common import resolve_artifact_or_exit
from phd_artifacts.cli.remotes.common import resolve_remote_name
from phd_artifacts.cli.ui import activity, confirm, console
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

        return perform_push(prepared)

    except (
        RemoteNotFoundError,
        UnsupportedBackendError,
        ValueError,
        RuntimeError,
        FileNotFoundError,
    ) as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None


def push(
    name: str = typer.Argument(
        ...,
        help="Artifact name.",
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
        help="Overwrite the remote artifact if it differs.",
    ),
):
    """Push a promoted artifact to remote storage."""

    artifact = resolve_artifact_or_exit(
        console=console,
        name=name,
        version=version,
        project=project,
    )

    remote_name = resolve_remote_name(remote)

    result = _push_artifact(
        artifact=artifact,
        remote_name=remote_name,
        force=force,
    )

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
