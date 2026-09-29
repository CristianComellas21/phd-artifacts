import typer
from rich.console import Console

from phd_artifacts.projects.exceptions import ProjectNotFoundError
from phd_artifacts.projects.service import remove_project

console = Console()


def remove(
    name: str = typer.Argument(
        ...,
        help="Project name.",
    ),
):
    """Remove a registered project."""

    try:
        remove_project(name)
    except ProjectNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None

    console.print(f"[green]Project '{name}' removed.[/green]")
