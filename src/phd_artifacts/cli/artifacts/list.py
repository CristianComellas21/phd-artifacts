import typer
from rich.console import Console
from rich.table import Table

from phd_artifacts.artifacts import get_artifacts
from phd_artifacts.core.filtering import parse_duration

console = Console()


def list_artifacts(
    project: str | None = typer.Option(
        None,
        "--project",
        "-p",
        help="Filter by project.",
    ),
    artifact_type: str | None = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by artifact type.",
    ),
    name: str | None = typer.Option(
        None,
        "--name",
        "-n",
        help="Filter by artifact name.",
    ),
    experiment: str | None = typer.Option(
        None,
        "--experiment",
        "-e",
        help="Filter by experiment name.",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        "-m",
        help="Filter by model name.",
    ),
    since: str | None = typer.Option(
        None,
        "--since",
        help="Show artifacts promoted within a duration such as 7d or 2w.",
    ),
):
    """List promoted artifacts."""

    try:
        since_delta = parse_duration(since) if since else None
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None

    artifacts = get_artifacts(
        artifact_type=artifact_type,
        project=project,
        name=name,
        experiment=experiment,
        model=model,
        since=since_delta,
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
