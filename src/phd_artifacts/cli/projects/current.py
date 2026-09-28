import typer
from rich.console import Console

from phd_artifacts.projects.service import get_current_project

console = Console()


def current():
    """Show the project corresponding to the current directory."""

    result = get_current_project()

    if result is None:
        console.print("[yellow]Current directory does not belong to a registered project.[/yellow]")
        raise typer.Exit(1)

    name, project = result

    console.print(f"[bold]{name}[/bold]")
    console.print(f"Root:      {project['root']}")
    console.print(f"Logs:      {project['logs']}")
    console.print(f"Artifacts: {project['workspace_artifacts']}")
