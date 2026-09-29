import typer
from rich.console import Console

from phd_artifacts.artifacts.transfer import push_artifact
from phd_artifacts.cli.artifacts.common import resolve_artifact_or_exit
from phd_artifacts.remotes.backends.exceptions import UnsupportedBackendError
from phd_artifacts.remotes.exceptions import RemoteNotFoundError

console = Console()


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
):
    """Push a promoted artifact to remote storage."""

    artifact = resolve_artifact_or_exit(
        console=console,
        name=name,
        version=version,
        project=project,
    )

    try:
        destination = push_artifact(
            artifact,
            remote_name=remote,
        )

    except (
        RemoteNotFoundError,
        UnsupportedBackendError,
        ValueError,
        RuntimeError,
        FileNotFoundError,
    ) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None

    console.print(f"\n[green]Artifact '{artifact.name}' pushed successfully.[/green]")
    console.print(f"Remote:      {remote}")
    console.print(f"Destination: {destination}")
