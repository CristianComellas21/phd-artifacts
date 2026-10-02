import typer

from phd_artifacts.cli.ui import confirm, console
from phd_artifacts.projects.exceptions import ProjectNotFoundError
from phd_artifacts.projects.service import remove_project


def remove(
    name: str = typer.Argument(
        ...,
        help="Project name.",
    ),
):
    """Remove a registered project."""

    if not confirm(
        f"Remove project '{name}'?",
        default=False,
    ):
        raise typer.Exit(0)

    try:
        remove_project(name)
    except ProjectNotFoundError as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None

    console.print(f"[success]Project '{name}' removed.[/success]")
