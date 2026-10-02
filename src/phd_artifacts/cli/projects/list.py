from rich.table import Table

from phd_artifacts.cli.ui import console
from phd_artifacts.projects.service import list_projects


def list_projects_command():
    """List registered projects."""

    projects = list_projects()

    if not projects:
        console.print("No projects registered.")
        return

    table = Table(
        "Name",
        "Root",
        "Python",
        "Exporter",
    )

    for name, project in projects.items():
        table.add_row(
            name,
            project["root"],
            project.get("python", ""),
            project.get("exporter", ""),
        )

    console.print(table)
