import typer
from rich.console import Console
from rich.table import Table

from phd_artifacts.core.filtering import parse_duration
from phd_artifacts.projects.exceptions import ProjectError
from phd_artifacts.projects.service import resolve_project
from phd_artifacts.runs import get_runs

console = Console()


def list_runs(
    project: str | None = typer.Option(
        None,
        "--project",
        "-p",
        help="Project name. Defaults to the current project.",
    ),
    limit: int = typer.Option(
        20,
        "--limit",
        "-n",
        help="Maximum number of runs to show.",
    ),
    include_tests: bool = typer.Option(
        False,
        "--tests",
        help="Include test runs.",
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
    checkpoints_only: bool = typer.Option(
        False,
        "--checkpoints",
        help="Show only runs containing checkpoints.",
    ),
    since: str | None = typer.Option(
        None,
        "--since",
        help="Show runs newer than a duration such as 24h, 7d or 2w.",
    ),
    show_all: bool = typer.Option(
        False,
        "--all",
        help="Show all matching runs.",
    ),
):
    """List detected Hydra runs."""

    try:
        since_delta = parse_duration(since) if since else None
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None

    try:
        project_name, _ = resolve_project(project)

        runs = get_runs(
            project=project_name,
            experiment=experiment,
            model=model,
            checkpoints_only=checkpoints_only,
            since=since_delta,
            include_tests=include_tests,
        )

    except ProjectError as exc:
        message = exc.args[0] if exc.args else str(exc)
        console.print(f"[red]{message}[/red]")
        raise typer.Exit(1) from None

    if not runs:
        console.print(f"No matching Hydra runs found for project '[bold]{project_name}[/bold]'.")
        return

    table = Table(
        "ID",
        "Experiment",
        "Model",
        "Created",
        "CKPT",
    )

    visible_runs = runs if show_all else runs[:limit]

    for run in visible_runs:
        table.add_row(
            run.id,
            run.experiment or "-",
            run.model or "-",
            (run.created_at.strftime("%Y-%m-%d %H:%M") if run.created_at else "-"),
            "yes" if run.has_checkpoints else "",
        )

    console.print(f"[bold]{project_name}[/bold]")
    console.print(table)

    if not show_all and len(runs) > limit:
        console.print(f"[dim]Showing {limit} of {len(runs)} matching runs.[/dim]")
