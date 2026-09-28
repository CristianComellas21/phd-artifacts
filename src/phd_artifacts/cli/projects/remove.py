import typer
from rich.console import Console

from phd_artifacts.projects import remove_project


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
    except KeyError:
        console.print(
            f"[red]Project '{name}' does not exist.[/red]"
        )
        raise typer.Exit(1)

    console.print(
        f"[green]Project '{name}' removed.[/green]"
    )