import typer

from phd_artifacts.artifacts import PushAction, RemoteArtifactConflictError, push_artifact
from phd_artifacts.cli.artifacts.common import resolve_artifact_or_exit
from phd_artifacts.cli.ui import console
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

    try:
        result = push_artifact(
            artifact,
            remote_name=remote,
            force=force,
        )

    except (
        RemoteArtifactConflictError,
        RemoteNotFoundError,
        UnsupportedBackendError,
        ValueError,
        RuntimeError,
        FileNotFoundError,
    ) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None

    match result.action:
        case PushAction.UPLOADED:
            console.print(f"\n[green]Artifact '{artifact.name}' uploaded successfully.[/green]")

        case PushAction.ALREADY_UP_TO_DATE:
            console.print(f"\n[green]Artifact '{artifact.name}' is already up to date.[/green]")

        case PushAction.OVERWRITTEN:
            console.print(
                f"\n[yellow]Artifact '{artifact.name}' overwritten successfully.[/yellow]"
            )

    console.print(f"Remote:      {remote}")
    console.print(f"Destination: {result.destination}")
