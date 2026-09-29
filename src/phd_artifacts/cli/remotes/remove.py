import typer
from rich.console import Console

from phd_artifacts.remotes import remove_remote

console = Console()


def remove(
    name: str = typer.Argument(
        ...,
        help="Remote name.",
    ),
):
    """Remove a configured artifact remote."""

    try:
        remove_remote(name)
    except KeyError:
        console.print(f"[red]Remote '{name}' not found.[/red]")
        raise typer.Exit(1) from None

    console.print(f"[green]Removed remote '{name}'.[/green]")
