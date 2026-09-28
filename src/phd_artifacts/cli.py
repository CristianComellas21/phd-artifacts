from pathlib import Path

import typer
from rich.console import Console

from phd_artifacts.config import (
    config_exists,
    create_config,
    get_config_path,
)


app = typer.Typer(
    name="phd-artifact",
    help="Manage research artifacts across projects and machines.",
)

console = Console()


@app.callback()
def main():
    """Manage research artifacts across projects and machines."""
    pass


@app.command()
def version():
    """Show the current version."""
    console.print("phd-artifacts 0.1.0")


@app.command()
def init(
    artifact_root: Path = typer.Option(
        ...,
        "--artifact-root",
        "-r",
        help="Root directory for promoted research artifacts.",
    ),
):
    """Initialize phd-artifacts on this machine."""

    config_path = get_config_path()

    if config_exists():
        overwrite = typer.confirm(
            f"Configuration already exists at {config_path}. Overwrite it?"
        )

        if not overwrite:
            raise typer.Exit()

    artifact_root = artifact_root.expanduser().resolve()
    artifact_root.mkdir(parents=True, exist_ok=True)

    create_config(artifact_root)

    console.print("[green]Configuration created successfully.[/green]")
    console.print(f"Config:   {config_path}")
    console.print(f"Artifacts: {artifact_root}")