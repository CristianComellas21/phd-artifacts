import typer

from phd_artifacts.artifacts.remote_index import rebuild_remote_index
from phd_artifacts.cli.remotes.common import resolve_remote_name
from phd_artifacts.cli.ui import activity, console
from phd_artifacts.remotes.backends.exceptions import UnsupportedBackendError
from phd_artifacts.remotes.exceptions import RemoteNotFoundError


def rebuild_index(
    remote: str | None = typer.Argument(
        None,
        help="Remote name.",
    ),
):
    """Rebuild the artifact index for a remote."""

    remote_name = resolve_remote_name(remote)

    try:
        with activity(f"Rebuilding index for '{remote_name}'"):
            index = rebuild_remote_index(
                remote_name=remote_name,
            )

    except (
        RemoteNotFoundError,
        UnsupportedBackendError,
        RuntimeError,
        ValueError,
    ) as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None

    console.print(
        f"[success]Indexed {len(index.artifacts)} artifacts on '{remote_name}'.[/success]"
    )
