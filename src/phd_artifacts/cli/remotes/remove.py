import typer
from rich.console import Console

from phd_artifacts.remotes import remove_remote
from phd_artifacts.remotes.exceptions import RemoteNotFoundError

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
    except RemoteNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None

    console.print(f"[green]Removed remote '{name}'.[/green]")
