import typer
from rich.console import Console

from phd_artifacts.artifacts.transfer import (
    get_artifact_remote_status,
)
from phd_artifacts.cli.artifacts.common import (
    resolve_artifact_or_exit,
)
from phd_artifacts.remotes.exceptions import RemoteError
from phd_artifacts.remotes.status import RemoteStatus

console = Console()


def status(
    name: str = typer.Argument(
        ...,
        help="Artifact name.",
    ),
    remote: str = typer.Option(
        ...,
        "--remote",
        "-r",
        help="Remote to check.",
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
    """Show the remote status of a promoted artifact."""

    artifact = resolve_artifact_or_exit(
        console=console,
        name=name,
        version=version,
        project=project,
    )

    try:
        comparison = get_artifact_remote_status(
            artifact,
            remote_name=remote,
        )
    except (RemoteError, RuntimeError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None

    console.print(f"[bold]{artifact.name}[/bold]\n")
    console.print(f"Project:  {artifact.project}")
    console.print(f"Version:  {artifact.version}")
    console.print(f"Remote:   {remote}")

    match comparison.status:
        case RemoteStatus.UP_TO_DATE:
            console.print("Status:   [green]up to date[/green]")

        case RemoteStatus.MISSING:
            console.print("Status:   [yellow]missing[/yellow]")

        case RemoteStatus.DIFFERENT:
            console.print("Status:   [red]different[/red]")
