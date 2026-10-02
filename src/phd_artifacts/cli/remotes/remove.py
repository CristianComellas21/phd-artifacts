import typer

from phd_artifacts.cli.remotes.common import resolve_remote_name
from phd_artifacts.cli.ui import confirm, console
from phd_artifacts.remotes import remove_remote
from phd_artifacts.remotes.exceptions import RemoteNotFoundError


def remove(
    name: str | None = typer.Argument(
        None,
        help="Remote name.",
    ),
):
    """Remove a configured artifact remote."""

    name = resolve_remote_name(
        name,
        auto_select_single=False,
    )

    if not confirm(
        f"Remove remote '{name}'?",
        default=False,
    ):
        raise typer.Exit(0)

    try:
        remove_remote(name)
    except RemoteNotFoundError as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None

    console.print(f"[success]Removed remote '{name}'.[/success]")
