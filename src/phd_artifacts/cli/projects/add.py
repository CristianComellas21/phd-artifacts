from pathlib import Path

import typer
from rich.console import Console

from phd_artifacts.projects import add_project

console = Console()


def add(
    name: str = typer.Argument(...),
    root: Path = typer.Argument(Path(".")),
    logs: Path | None = typer.Option(None, "--logs"),
    workspace_artifacts: Path | None = typer.Option(None, "--artifacts"),
):
    """Register a project."""

    project = add_project(
        name=name,
        root=root,
        logs=logs,
        workspace_artifacts=workspace_artifacts,
    )

    console.print(f"[green]Project '{name}' added.[/green]")
    console.print(f"Root:      {project['root']}")
    console.print(f"Logs:      {project['logs']}")
    console.print(f"Artifacts: {project['workspace_artifacts']}")
