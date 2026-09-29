import typer
from rich.console import Console
from rich.table import Table

from phd_artifacts.artifacts import Artifact, get_artifact
from phd_artifacts.artifacts.exceptions import (
    ArtifactAmbiguousError,
    ArtifactNotFoundError,
)


def resolve_artifact_or_exit(
    console: Console,
    name: str,
    version: str | None = None,
    project: str | None = None,
) -> Artifact:
    """Resolve exactly one artifact or display a CLI error and exit."""

    try:
        return get_artifact(
            name=name,
            version=version,
            project=project,
        )

    except ArtifactNotFoundError as exc:
        console.print(f"[red]Artifact '{exc.name}' not found.[/red]")
        raise typer.Exit(1) from None

    except ArtifactAmbiguousError as exc:
        console.print(f"[yellow]Multiple versions found for '{exc.name}'.[/yellow]")

        table = Table(
            "Version",
            "Project",
            "Promoted",
        )

        for artifact in exc.artifacts:
            table.add_row(
                artifact.version,
                artifact.project,
                artifact.metadata.get("promoted_at", "-"),
            )

        console.print(table)

        console.print("\nSpecify one with [bold]--version[/bold].")

        raise typer.Exit(1) from None
