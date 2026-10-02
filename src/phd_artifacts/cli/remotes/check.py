import typer

from phd_artifacts.cli.remotes.common import resolve_remote_name
from phd_artifacts.cli.ui import console
from phd_artifacts.remotes import check_remote
from phd_artifacts.remotes.exceptions import RemoteNotFoundError


def check(
    name: str = typer.Argument(
        ...,
        help="Remote name.",
    ),
):
    """Check that a remote is configured and accessible."""

    remote_name = resolve_remote_name(name)

    try:
        remote = check_remote(remote_name)
    except (RemoteNotFoundError, ValueError, RuntimeError) as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None

    console.print(f"[success]Remote '{remote.name}' is available.[/success]")
    console.print(f"Type:   {remote.type}")
    console.print(f"Target: {remote.target}")
