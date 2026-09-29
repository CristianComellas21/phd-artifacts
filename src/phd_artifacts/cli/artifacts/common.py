import typer
from rich.console import Console
from rich.table import Table

from phd_artifacts.artifacts import Artifact, get_artifact
from phd_artifacts.artifacts.exceptions import (
    ArtifactAmbiguousError,
    ArtifactNotFoundError,
)
from phd_artifacts.cli.artifacts.queries import get_artifacts


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
        matches = get_artifacts(
            name=exc.name,
            project=project,
        )

        if matches:
            console.print(f"[red]Artifact '{exc.name}' not found.[/red]\n")
            console.print("[yellow]Possible matches:[/yellow]")

            names = sorted({artifact.name for artifact in matches})

            for candidate in names:
                console.print(f"  {candidate}")
        else:
            console.print(f"[red]Artifact '{exc.name}' not found.[/red]")

        raise typer.Exit(1) from None

    except ArtifactAmbiguousError as exc:
        console.print(f"[yellow]Multiple versions found for '{exc.name}'.[/yellow]")

        table = Table(
            "#",
            "Version",
            "Project",
            "Promoted",
        )

        for index, artifact in enumerate(exc.artifacts, start=1):
            table.add_row(
                str(index),
                artifact.version,
                artifact.project,
                artifact.metadata.get("promoted_at", "-"),
            )

        console.print(table)

        selection = typer.prompt(
            "Select version",
            type=int,
            default=1,
        )

        if selection < 1 or selection > len(exc.artifacts):
            console.print("[red]Invalid selection.[/red]")
            raise typer.Exit(1) from None

        return exc.artifacts[selection - 1]
