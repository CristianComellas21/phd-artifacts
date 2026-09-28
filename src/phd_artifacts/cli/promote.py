from pathlib import Path

import typer
from rich.console import Console

from phd_artifacts.artifacts import promote_checkpoint
from phd_artifacts.runs import get_run, get_run_checkpoints

console = Console()


def promote(
    run_id: str = typer.Argument(
        ...,
        help="Run ID to promote.",
    ),
    name: str = typer.Option(
        ...,
        "--name",
        "-n",
        help="Human-readable artifact name.",
    ),
    checkpoint: str | None = typer.Option(
        None,
        "--checkpoint",
        "-c",
        help="Checkpoint filename or relative path.",
    ),
    project: str | None = typer.Option(
        None,
        "--project",
        "-p",
        help="Project name. Defaults to the current project.",
    ),
):
    """Promote a run checkpoint to the persistent artifact store."""

    try:
        project_name, _, run = get_run(
            run_id,
            project_name=project,
        )
    except (KeyError, RuntimeError) as exc:
        console.print(f"[red]{exc.args[0]}[/red]")
        raise typer.Exit(1) from None

    checkpoints = get_run_checkpoints(run)

    if not checkpoints:
        console.print("[red]This run contains no checkpoints.[/red]")
        raise typer.Exit(1)

    selected: Path

    if checkpoint is not None:
        matches = [
            path
            for path in checkpoints
            if path.name == checkpoint or str(path.relative_to(run.path)) == checkpoint
        ]

        if not matches:
            console.print(f"[red]Checkpoint '{checkpoint}' not found.[/red]")
            raise typer.Exit(1)

        selected = matches[0]

    elif len(checkpoints) == 1:
        selected = checkpoints[0]

    else:
        console.print("[bold]Available checkpoints:[/bold]")

        for index, path in enumerate(checkpoints, start=1):
            size_mb = path.stat().st_size / (1024**2)

            console.print(f"  {index}. {path.name} ({size_mb:.1f} MB)")

        choice = typer.prompt(
            "Select checkpoint",
            type=int,
        )

        if choice < 1 or choice > len(checkpoints):
            console.print("[red]Invalid selection.[/red]")
            raise typer.Exit(1)

        selected = checkpoints[choice - 1]

    try:
        destination = promote_checkpoint(
            project_name=project_name,
            run=run,
            checkpoint=selected,
            name=name,
        )
    except FileExistsError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None

    console.print("\n[green]Checkpoint promoted successfully.[/green]")
    console.print(f"Run:        {run.id}")
    console.print(f"Checkpoint: {selected.name}")
    console.print(f"Artifact:   {destination}")
