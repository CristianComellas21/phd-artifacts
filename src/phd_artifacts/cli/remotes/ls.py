import typer
from rich.table import Table

from phd_artifacts.cli.remotes.common import resolve_remote_name
from phd_artifacts.cli.ui import console
from phd_artifacts.core.display import format_size
from phd_artifacts.remotes import list_remote
from phd_artifacts.remotes.backends.exceptions import (
    UnsupportedBackendError,
)
from phd_artifacts.remotes.exceptions import RemoteError


def ls(
    name: str = typer.Argument(
        ...,
        help="Remote name.",
    ),
    path: str | None = typer.Argument(
        None,
        help="Path relative to the configured remote target.",
    ),
):
    """List files and directories on a remote."""

    remote_name = resolve_remote_name(name)

    try:
        entries = list_remote(
            name=remote_name,
            path=path or "",
        )

    except (
        RemoteError,
        UnsupportedBackendError,
        RuntimeError,
        ValueError,
    ) as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None

    if not entries:
        console.print("Remote directory is empty.")
        return

    table = Table(
        "Type",
        "Name",
        "Size",
    )

    for entry in entries:
        table.add_row(
            "dir" if entry.is_dir else "file",
            entry.name,
            ("-" if entry.size is None else format_size(entry.size)),
        )

    console.print(table)
