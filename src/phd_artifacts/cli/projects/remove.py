import typer

from phd_artifacts.cli.ui import console
from phd_artifacts.projects.exceptions import ProjectNotFoundError
from phd_artifacts.projects.service import remove_project


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
