import typer
from rich.console import Console

from phd_artifacts.runs import Run, get_run
from phd_artifacts.runs.exceptions import (
    RunAmbiguousError,
    RunNotFoundError,
)


def resolve_run_or_exit(
    console: Console,
    run_id: str,
    project: str | None = None,
) -> Run:
    """Resolve exactly one run or display a CLI error and exit."""

    try:
        return get_run(
            run_id=run_id,
            project=project,
        )

    except RunNotFoundError as exc:
        console.print(f"[red]Run '{exc.run_id}' not found.[/red]")
        raise typer.Exit(1) from None

    except RunAmbiguousError as exc:
        console.print(f"[red]Run ID '{exc.run_id}' is ambiguous.[/red]")

        for run in exc.runs:
            console.print(f"  {run.project}: {run.relative_path}")

        raise typer.Exit(1) from None
