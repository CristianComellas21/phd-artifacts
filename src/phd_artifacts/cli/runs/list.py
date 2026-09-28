import typer
from rich.console import Console
from rich.table import Table

from phd_artifacts.runs import get_project_runs

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
):
    """List detected Hydra runs."""

    try:
        project_name, _, runs = get_project_runs(
            project_name=project,
            include_tests=include_tests,
        )
    except (KeyError, RuntimeError) as exc:
        message = exc.args[0] if exc.args else str(exc)
        console.print(f"[red]{message}[/red]")
        raise typer.Exit(1) from None

    if not runs:
        console.print(f"No Hydra runs found for project '[bold]{project_name}[/bold]'.")
        return

    table = Table(
        "ID",
        "Experiment",
        "Model",
        "Created",
        "CKPT",
    )

    for run in runs[:limit]:
        table.add_row(
            run.id,
            run.experiment or "-",
            run.model or "-",
            (run.created_at.strftime("%Y-%m-%d %H:%M") if run.created_at else "-"),
            "yes" if run.has_checkpoints else "",
        )

    console.print(f"[bold]{project_name}[/bold]")
    console.print(table)

    if len(runs) > limit:
        console.print(f"[dim]Showing {limit} of {len(runs)} runs.[/dim]")
