import typer
from rich.console import Console

from phd_artifacts.projects.exceptions import ProjectNotResolvedError
from phd_artifacts.projects.service import resolve_project

console = Console()


def current():
    """Show the current project."""

    try:
        name, project = resolve_project()

    except ProjectNotResolvedError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None

    console.print(f"[bold]{name}[/bold]")
    console.print(f"Root:      {project['root']}")
    console.print(f"Logs:      {project['logs']}")
    console.print(f"Artifacts: {project['workspace_artifacts']}")

    if python_path := project.get("python"):
        console.print(f"Python:    {python_path}")

    if exporter := project.get("exporter"):
        console.print(f"Exporter:  {exporter}")

    exporter_args = project.get("exporter_args")

    if exporter_args:
        console.print(f"Args:      {' '.join(exporter_args)}")
