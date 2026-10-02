from pathlib import Path

import typer
from rich.console import Console

from phd_artifacts.cli.projects.common import prompt_project_config
from phd_artifacts.projects.service import add_project

console = Console()


def add(
    name: str = typer.Argument(
        ...,
        help="Project name.",
    ),
    root: Path = typer.Option(
        None,
        "--root",
        "-r",
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
        help="Python executable used for project-specific tools.",
    ),
    exporter: str | None = typer.Option(
        None,
        "--exporter",
        help="Portable weight exporter, relative to the project root.",
    ),
    exporter_arg: list[str] | None = typer.Option(
        None,
        "--exporter-arg",
        help=("Argument passed to the exporter. Can be repeated."),
    ),
):
    """Register a research project."""

    if root is None:
        values = prompt_project_config()

        root = values.root
        logs = values.logs
        workspace_artifacts = values.workspace_artifacts
        python = values.python
        exporter = values.exporter
        exporter_arg = values.exporter_args

    try:
        project = add_project(
            name=name,
            root=root,
            logs=logs,
            workspace_artifacts=workspace_artifacts,
            python=python,
            exporter=exporter,
            exporter_args=exporter_arg,
        )

    except (
        ValueError,
        FileNotFoundError,
    ) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None

    console.print(f"[green]Project '{name}' registered.[/green]")

    console.print(f"Root:      {project['root']}")
    console.print(f"Logs:      {project['logs']}")
    console.print(f"Artifacts: {project['workspace_artifacts']}")

    if python_path := project.get("python"):
        console.print(f"Python:    {python_path}")

    if exporter_path := project.get("exporter"):
        console.print(f"Exporter:  {exporter_path}")

    exporter_args = project.get("exporter_args")

    if exporter_args:
        console.print(f"Args:      {' '.join(exporter_args)}")
