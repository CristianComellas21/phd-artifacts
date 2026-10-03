import typer

from phd_artifacts.cli.remotes.common import resolve_remote_name
from phd_artifacts.cli.ui import console
from phd_artifacts.remotes import tree_remote
from phd_artifacts.remotes.backends.exceptions import (
    UnsupportedBackendError,
)
from phd_artifacts.remotes.exceptions import RemoteError


def tree(
    name: str = typer.Argument(
        None,
        help="Remote name.",
    ),
    path: str | None = typer.Argument(
        None,
        help="Path relative to the configured remote target.",
    ),
    depth: int | None = typer.Option(
        None,
        "--depth",
        "-d",
        min=0,
        help="Maximum directory depth.",
    ),
    dirs_only: bool = typer.Option(
        False,
        "--dirs-only",
        help="Show directories only.",
    ),
):
    """Show a remote directory tree."""

    remote_name = resolve_remote_name(name)

    try:
        entries = tree_remote(
            name=remote_name,
            path=path or "",
            max_depth=depth,
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

    for item in entries:
        if dirs_only and not item.entry.is_dir:
            continue

        prefix = "    " * item.depth
        marker = "📁" if item.entry.is_dir else "📄"

        console.print(f"{prefix}{marker} {item.entry.name}")
