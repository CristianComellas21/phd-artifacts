import typer
from rich.console import Console

from phd_artifacts.remotes import check_remote

console = Console()


def check(
    name: str = typer.Argument(
        ...,
        help="Remote name.",
    ),
):
    """Check that a remote is configured and accessible."""

    try:
        remote = check_remote(name)
    except (KeyError, ValueError, RuntimeError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None

    console.print(f"[green]Remote '{remote.name}' is available.[/green]")
    console.print(f"Type:   {remote.type}")
    console.print(f"Target: {remote.target}")
