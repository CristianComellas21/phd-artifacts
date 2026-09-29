import typer
from rich.console import Console

from phd_artifacts.remotes import tree_remote
from phd_artifacts.remotes.backends.exceptions import (
    UnsupportedBackendError,
)
from phd_artifacts.remotes.exceptions import RemoteError

console = Console()


def tree(
    name: str = typer.Argument(
        ...,
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

    try:
        entries = tree_remote(
            name=name,
            path=path or "",
            max_depth=depth,
        )
    except (
        RemoteError,
        UnsupportedBackendError,
        RuntimeError,
        ValueError,
    ) as exc:
        console.print(f"[red]{exc}[/red]")
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
