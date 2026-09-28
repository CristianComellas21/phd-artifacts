from rich.console import Console
from rich.table import Table

from phd_artifacts.projects.service import list_projects as get_projects

console = Console()


def list_projects():
    """List registered projects."""

    projects = get_projects()

    if not projects:
        console.print("No projects registered.")
        return

    table = Table(
        "Project",
        "Root",
        "Logs",
        "Artifacts",
    )

    for name, project in projects.items():
        table.add_row(
            name,
            project["root"],
            project["logs"],
            project["workspace_artifacts"],
        )

    console.print(table)
