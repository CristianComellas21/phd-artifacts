import typer

from phd_artifacts.artifacts import PushAction, RemoteArtifactConflictError, push_artifact
from phd_artifacts.cli.artifacts.common import resolve_artifact_or_exit
from phd_artifacts.cli.remotes.common import resolve_remote_name
from phd_artifacts.cli.ui import confirm, console
from phd_artifacts.remotes.backends.exceptions import UnsupportedBackendError
from phd_artifacts.remotes.exceptions import RemoteNotFoundError


def push(
    name: str = typer.Argument(
        ...,
        help="Artifact name.",
    ),
    remote: str = typer.Option(
        ...,
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

    try:
        result = push_artifact(
            artifact,
            remote_name=remote_name,
            force=force,
        )

    except RemoteArtifactConflictError as exc:
        if force:
            console.print(f"[error]{exc}[/error]")
            raise typer.Exit(1) from None

        if not confirm(
            f"Remote artifact '{artifact.name}' differs. Overwrite remote copy?",
            default=False,
        ):
            raise typer.Exit(0) from None

        result = push_artifact(
            artifact=artifact,
            remote_name=remote_name,
            force=True,
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

    match result.action:
        case PushAction.UPLOADED:
            console.print(f"\n[success]Artifact '{artifact.name}' uploaded successfully.[/success]")

        case PushAction.ALREADY_UP_TO_DATE:
            console.print(f"\n[success]Artifact '{artifact.name}' is already up to date.[/success]")

        case PushAction.OVERWRITTEN:
            console.print(
                f"\n[warning]Artifact '{artifact.name}' overwritten successfully.[/warning]"
            )

    console.print(f"Remote:      {remote}")
    console.print(f"Destination: {result.destination}")
