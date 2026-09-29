from pathlib import Path

from rich.console import Console
from rich.syntax import Syntax


def print_yaml_file(
    console: Console,
    path: Path,
    title: str,
) -> None:
    """Print a YAML file with syntax highlighting."""

    console.print(f"\n[bold]{title}[/bold]")

    if not path.exists():
        console.print("[yellow]Not available.[/yellow]")
        return

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        console.print(f"[red]Could not read {path}: {exc}[/red]")
        return

    syntax = Syntax(
        content,
        "yaml",
        word_wrap=False,
    )

    console.print(syntax)


def format_size(size: int) -> str:
    value = float(size)

    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"

        value /= 1024

    return f"{size} B"
