import typer

from phd_artifacts.cli.artifacts.common import (
    resolve_artifact_or_exit,
    resolve_checkpoint_role,
)
from phd_artifacts.cli.ui import console


def path(
    name: str = typer.Argument(
        ...,
        help="Artifact name.",
    ),
    checkpoint: str | None = typer.Option(
        None,
        "--checkpoint",
        "-c",
        help="Checkpoint role.",
    ),
    version: str | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Artifact version.",
    ),
    project: str | None = typer.Option(
        None,
        "--project",
        "-p",
        help="Project name.",
    ),
    relative: bool = typer.Option(
        False,
        "--relative",
        help="Show path relative to the artifact directory.",
    ),
):
    """Show the path to a promoted checkpoint."""

    artifact = resolve_artifact_or_exit(
        console=console,
        name=name,
        version=version,
        project=project,
    )

    role = resolve_checkpoint_role(
        artifact=artifact,
        role=checkpoint,
    )

    if relative:
        checkpoint_path = artifact.checkpoint_relative_path(role)
    else:
        checkpoint_path = artifact.checkpoint_path(role)

    console.print(str(checkpoint_path))
