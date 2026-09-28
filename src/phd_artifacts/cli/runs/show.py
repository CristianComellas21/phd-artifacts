import typer
from rich.console import Console
from rich.table import Table

from phd_artifacts.runs import get_run, get_run_checkpoints

console = Console()


def show_run(
    run_id: str = typer.Argument(..., help="Run ID."),
    project: str | None = typer.Option(
        None,
        "--project",
        "-p",
        help="Project name. Defaults to the current project.",
    ),
):
    """Show detailed information about a run."""

    try:
        project_name, _, run = get_run(
            run_id,
            project_name=project,
        )
    except (KeyError, RuntimeError) as exc:
        console.print(f"[red]{exc.args[0]}[/red]")
        raise typer.Exit(1) from None

    console.print(f"[bold]Run {run.id}[/bold]\n")

    console.print(f"Project:    {project_name}")
    console.print(f"Experiment: {run.experiment or '-'}")
    console.print(f"Model:      {run.model or '-'}")

    if run.created_at:
        console.print(f"Created:    {run.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

    console.print(f"Path:       {run.path}")

    hydra_dir = run.path / ".hydra"

    console.print("\n[bold]Hydra[/bold]")

    for filename in ("config.yaml", "overrides.yaml", "hydra.yaml"):
        path = hydra_dir / filename

        if path.exists():
            console.print(f"  {filename}: {path}")

    checkpoints = get_run_checkpoints(run)

    console.print("\n[bold]Checkpoints[/bold]")

    if not checkpoints:
        console.print("  None")
        return

    table = Table("#", "Name", "Size")

    for index, checkpoint in enumerate(checkpoints, start=1):
        size_mb = checkpoint.stat().st_size / (1024**2)

        table.add_row(
            str(index),
            str(checkpoint.relative_to(run.path)),
            f"{size_mb:.1f} MB",
        )

    console.print(table)
