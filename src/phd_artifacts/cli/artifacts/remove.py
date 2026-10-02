import typer

from phd_artifacts.artifacts import remove_artifact
from phd_artifacts.cli.artifacts.common import resolve_artifact_or_exit
from phd_artifacts.cli.ui import confirm, console


def remove(
    name: str = typer.Argument(..., help="Artifact name."),
    project: str | None = typer.Option(
        None,
        "--project",
        "-p",
        help="Project name.",
    ),
    version: str | None = typer.Option(
        None,
        "--version",
        "-v",
        help="Artifact version.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Remove without confirmation.",
    ),
):
    """Remove a local promoted artifact."""

    artifact = resolve_artifact_or_exit(
        console=console,
        name=name,
        version=version,
        project=project,
    )

    if not yes:
        confirmed = confirm(
            f"Remove artifact '{artifact.name}' version '{artifact.version}'?",
            default=False,
        )

        if not confirmed:
            raise typer.Exit(0)

    remove_artifact(artifact)

    console.print(
        f"[success]Removed artifact '{artifact.name}' version '{artifact.version}'.[/success]"
    )
