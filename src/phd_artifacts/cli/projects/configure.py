from pathlib import Path

import typer
from rich.console import Console

from phd_artifacts.projects.exceptions import ProjectNotFoundError
from phd_artifacts.projects.service import update_project

console = Console()


def configure(
    name: str = typer.Argument(
        ...,
        help="Project name.",
    ),
    root: Path | None = typer.Option(
        None,
        "--root",
        help="Project root directory.",
    ),
    logs: Path | None = typer.Option(
        None,
        "--logs",
        help="Hydra logs directory.",
    ),
    workspace_artifacts: Path | None = typer.Option(
        None,
        "--workspace-artifacts",
        help="Project-local artifact workspace.",
    ),
    python: Path | None = typer.Option(
        None,
        "--python",
        help="Python executable for project-specific tools.",
    ),
    exporter: str | None = typer.Option(
        None,
        "--exporter",
        help="Exporter path relative to the project root.",
    ),
    exporter_arg: list[str] | None = typer.Option(
        None,
        "--exporter-arg",
        help="Exporter argument. Can be repeated.",
    ),
    clear_python: bool = typer.Option(
        False,
        "--clear-python",
        help="Remove the configured Python executable.",
    ),
    clear_exporter: bool = typer.Option(
        False,
        "--clear-exporter",
        help="Remove exporter and exporter arguments.",
    ),
):
    """Update a project configuration."""

    if python is not None and clear_python:
        console.print("[red]Cannot use --python and --clear-python together.[/red]")
        raise typer.Exit(1)

    if exporter is not None and clear_exporter:
        console.print("[red]Cannot use --exporter and --clear-exporter together.[/red]")
        raise typer.Exit(1)

    try:
        project = update_project(
            name=name,
            root=root,
            logs=logs,
            workspace_artifacts=workspace_artifacts,
            python=python,
            exporter=exporter,
            exporter_args=exporter_arg,
            clear_python=clear_python,
            clear_exporter=clear_exporter,
        )

    except (
        ProjectNotFoundError,
        FileNotFoundError,
        ValueError,
    ) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None

    console.print(f"[green]Project '{name}' updated.[/green]\n")

    console.print(f"Root:      {project['root']}")
    console.print(f"Logs:      {project['logs']}")
    console.print(f"Artifacts: {project['workspace_artifacts']}")
    console.print(f"Python:    {project.get('python', '-')}")
    console.print(f"Exporter:  {project.get('exporter', '-')}")

    exporter_args = project.get("exporter_args", [])

    console.print(f"Args:      {' '.join(exporter_args) if exporter_args else '-'}")
