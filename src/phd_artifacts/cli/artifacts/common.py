import typer
from rich.console import Console
from rich.table import Table

from phd_artifacts.artifacts import Artifact, get_artifact, get_remote_artifact
from phd_artifacts.artifacts.exceptions import (
    ArtifactAmbiguousError,
    ArtifactNotFoundError,
    RemoteArtifactAmbiguousError,
    RemoteArtifactNotFoundError,
)
from phd_artifacts.artifacts.models import RemoteArtifact
from phd_artifacts.artifacts.queries import get_artifacts


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
            console.print(f"[error]Artifact '{exc.name}' not found.[/error]\n")
            console.print("[warning]Possible matches:[/warning]")

            names = sorted({artifact.name for artifact in matches})

            for candidate in names:
                console.print(f"  {candidate}")
        else:
            console.print(f"[error]Artifact '{exc.name}' not found.[/error]")

        raise typer.Exit(1) from None

    except ArtifactAmbiguousError as exc:
        console.print(f"[warning]Multiple versions found for '{exc.name}'.[/warning]")

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
            console.print("[error]Invalid selection.[/error]")
            raise typer.Exit(1) from None

        return exc.artifacts[selection - 1]


def resolve_remote_artifact_or_exit(
    console: Console,
    remote_name: str,
    name: str,
    project: str | None = None,
    version: str | None = None,
) -> RemoteArtifact:
    try:
        return get_remote_artifact(
            remote_name=remote_name,
            name=name,
            project=project,
            version=version,
        )

    except RemoteArtifactNotFoundError as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None

    except RemoteArtifactAmbiguousError as exc:
        artifacts = sorted(
            exc.artifacts,
            key=lambda artifact: artifact.version,
            reverse=True,
        )

        console.print(f"[accent]Multiple versions of '{name}' found on '{remote_name}':[/accent]")

        for index, artifact in enumerate(
            artifacts,
            start=1,
        ):
            console.print(f"  {index}. {artifact.version}")

        choice = typer.prompt(
            "Select version",
            type=int,
            default=1,
        )

        if choice < 1 or choice > len(artifacts):
            console.print("[error]Invalid selection.[/error]")
            raise typer.Exit(1) from None

        return artifacts[choice - 1]
