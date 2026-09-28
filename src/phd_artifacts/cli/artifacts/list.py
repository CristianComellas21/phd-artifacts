import typer
from rich.console import Console
from rich.table import Table

from phd_artifacts.artifacts import discover_artifacts

console = Console()


def list_artifacts(
    project: str | None = typer.Option(
        None,
        "--project",
        "-p",
        help="Filter by project.",
    ),
):
    """List promoted artifacts."""

    artifacts = discover_artifacts(
        project_name=project,
    )

    if not artifacts:
        console.print("No promoted artifacts found.")
        return

    table = Table(
        "Project",
        "Type",
        "Name",
        "Version",
    )

    for artifact in artifacts:
        table.add_row(
            artifact.project,
            artifact.artifact_type,
            artifact.name,
            artifact.version,
        )

    console.print(table)
