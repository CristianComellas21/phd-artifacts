import typer
from rich.table import Table

from phd_artifacts.cli.ui import console
from phd_artifacts.core.config_filtering import parse_config_filters
from phd_artifacts.core.filtering import parse_duration
from phd_artifacts.projects.exceptions import ProjectError
from phd_artifacts.projects.service import resolve_project
from phd_artifacts.runs import get_runs


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
    config: list[str] | None = typer.Option(
        None,
        "--config",
        help=(
            "Filter by Hydra config value. Can be repeated. "
            "Quote expressions, e.g. "
            "--config 'dataset.fixed_variance=15' or "
            "--config 'trainer.max_epochs>=10000'."
        ),
    ),
    config_any: list[str] | None = typer.Option(
        None,
        "--config-any",
        help=(
            "Filter by a config key found anywhere in the Hydra config. "
            "Can be repeated. Quote expressions, e.g. "
            "--config-any 'sigma=15'."
        ),
    ),
):
    """List detected Hydra runs."""

    try:
        since_delta = parse_duration(since) if since else None
    except ValueError as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None

    try:
        config_filters = parse_config_filters(config or [])
        config_any_filters = parse_config_filters(config_any or [])
    except ValueError as exc:
        console.print(f"[error]{exc}[/error]")
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
            config_filters=config_filters,
            config_any_filters=config_any_filters,
        )

    except ProjectError as exc:
        message = exc.args[0] if exc.args else str(exc)
        console.print(f"[error]{message}[/error]")
        raise typer.Exit(1) from None

    if not runs:
        console.print(
            f"No matching Hydra runs found for project '[accent]{project_name}[/accent]'."
        )
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
            (run.created_at.strftime("%Y-%m-%d %H:%M:%S") if run.created_at else "-"),
            "yes" if run.has_checkpoints else "",
        )

    console.print(f"[accent]{project_name}[/accent]")
    console.print(table)

    if not show_all and len(runs) > limit:
        console.print(f"[muted]Showing {limit} of {len(runs)} matching runs.[/muted]")
