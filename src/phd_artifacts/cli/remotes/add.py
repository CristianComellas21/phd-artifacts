import typer

from phd_artifacts.cli.ui import console
from phd_artifacts.remotes import add_remote


def add(
    name: str = typer.Argument(
        ...,
        help="Remote name.",
    ),
    remote_type: str = typer.Option(
        ...,
        "--type",
        help="Remote backend type.",
    ),
    target: str = typer.Option(
        ...,
        "--target",
        help="Remote storage target.",
    ),
):
    """Add a remote artifact store."""

    try:
        remote = add_remote(
            name=name,
            remote_type=remote_type,
            target=target,
        )
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None

    console.print(f"[green]Added remote '{remote.name}'.[/green]")
    console.print(f"Type:   {remote.type}")
    console.print(f"Target: {remote.target}")
