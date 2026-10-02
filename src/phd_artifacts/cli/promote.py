from pathlib import Path
from typing import cast

import questionary
import typer

from phd_artifacts.artifacts import promote_checkpoints
from phd_artifacts.artifacts.checkpoints import infer_checkpoint_role
from phd_artifacts.artifacts.models import CheckpointSelection
from phd_artifacts.cli.runs.common import resolve_run_or_exit
from phd_artifacts.cli.ui import checkbox, console
from phd_artifacts.runs import get_run_checkpoints


def _build_selections(
    checkpoints: list[Path],
) -> list[CheckpointSelection]:
    selections: list[CheckpointSelection] = []

    for path in checkpoints:
        role = infer_checkpoint_role(path)

        if role is None:
            role = typer.prompt(f"Role for {path.name}").strip()

        if not role:
            console.print(f"[error]Role cannot be empty for {path.name}.[/error]")
            raise typer.Exit(1)

        selections.append(
            CheckpointSelection(
                role=role,
                path=path,
            )
        )

    roles = [selection.role for selection in selections]

    if len(roles) != len(set(roles)):
        console.print("[error]Checkpoint roles must be unique.[/error]")
        raise typer.Exit(1)

    return selections


def _resolve_checkpoint_paths(
    requested: list[str],
    checkpoints: list[Path],
    run_path: Path,
) -> list[Path]:
    selected: list[Path] = []

    for checkpoint in requested:
        matches = [
            path
            for path in checkpoints
            if (path.name == checkpoint or str(path.relative_to(run_path)) == checkpoint)
        ]

        if not matches:
            console.print(f"[error]Checkpoint '{checkpoint}' not found.[/error]")
            raise typer.Exit(1)

        if len(matches) > 1:
            console.print(f"[error]Checkpoint '{checkpoint}' is ambiguous.[/error]")
            raise typer.Exit(1)

        selected.append(matches[0])

    return selected


def _select_checkpoints_interactively(
    checkpoints: list[Path],
) -> list[Path]:
    if len(checkpoints) == 1:
        return checkpoints

    choices = []

    for path in checkpoints:
        size_mb = path.stat().st_size / (1024**2)

        choices.append(
            questionary.Choice(
                title=f"{path.name} ({size_mb:.1f} MB)",
                value=path,
            )
        )

    selected = checkbox(
        "Select checkpoints to promote:",
        choices=choices,
    )

    if not selected:
        raise typer.Exit() from None

    return cast(list[Path], selected)


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
    checkpoint: list[str] | None = typer.Option(
        None,
        "--checkpoint",
        "-c",
        help=("Checkpoint filename or relative path. Can be repeated."),
    ),
    project: str | None = typer.Option(
        None,
        "--project",
        "-p",
        help=("Project name. Defaults to the current project."),
    ),
    no_export: bool = typer.Option(
        False,
        "--no-export",
        help="Skip automatic portable weight export.",
    ),
):
    """Promote run checkpoints to the persistent artifact store."""

    run = resolve_run_or_exit(
        console=console,
        run_id=run_id,
        project=project,
    )

    checkpoints = get_run_checkpoints(run)

    if not checkpoints:
        console.print("[error]This run contains no checkpoints.[/error]")
        raise typer.Exit(1)

    if checkpoint:
        selected_paths = _resolve_checkpoint_paths(
            requested=checkpoint,
            checkpoints=checkpoints,
            run_path=run.path,
        )
    else:
        selected_paths = _select_checkpoints_interactively(checkpoints)

    if len(selected_paths) != len(set(selected_paths)):
        console.print("[error]The same checkpoint cannot be selected more than once.[/error]")
        raise typer.Exit(1)

    selections = _build_selections(selected_paths)

    try:
        destination = promote_checkpoints(
            run=run,
            checkpoints=selections,
            name=name,
            no_export=no_export,
        )

    except FileExistsError as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None

    console.print("\n[success]Artifact promoted successfully.[/success]")
    console.print(f"Run:      {run.id}")
    console.print(f"Artifact: {destination}")
    console.print("Checkpoints:")

    for selection in selections:
        console.print(f"  {selection.role}: {selection.path.name}")
