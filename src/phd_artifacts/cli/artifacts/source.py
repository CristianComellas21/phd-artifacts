import typer

from phd_artifacts.cli.artifacts.common import (
    resolve_artifact_or_exit,
    resolve_checkpoint_role,
)
from phd_artifacts.cli.ui import console


def source(
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
):
    """Show the original source path of a promoted checkpoint."""

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

    console.print(str(artifact.checkpoint_source(role)))
