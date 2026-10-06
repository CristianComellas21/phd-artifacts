from typing import cast

import questionary
import typer
from rich.console import Console
from rich.table import Table

from phd_artifacts.artifacts import Artifact, RemoteArtifact, get_artifact, get_remote_artifact
from phd_artifacts.artifacts.exceptions import (
    ArtifactAmbiguousError,
    ArtifactNotFoundError,
    RemoteArtifactAmbiguousError,
    RemoteArtifactNotFoundError,
)
from phd_artifacts.artifacts.queries import get_artifacts, get_remote_artifacts
from phd_artifacts.cli.ui import select


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

        if not matches:
            console.print(f"[error]Artifact '{exc.name}' not found.[/error]")
            raise typer.Exit(1) from None

        console.print(f"[error]Artifact '{exc.name}' not found.[/error]\n")

        names = sorted({artifact.name for artifact in matches})

        selected_name = select(
            "Select a matching artifact:",
            [
                questionary.Choice(
                    title=candidate,
                    value=candidate,
                )
                for candidate in names
            ],
        )

        if selected_name is None:
            raise typer.Exit() from None

        return resolve_artifact_or_exit(
            console=console,
            name=cast(str, selected_name),
            version=version,
            project=project,
        )

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

        selected = select(
            "Select version:",
            [
                questionary.Choice(
                    title=artifact.version,
                    value=artifact,
                )
                for artifact in exc.artifacts
            ],
        )

        if selected is None:
            raise typer.Exit() from None

        return cast(Artifact, selected)


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
        matches = get_remote_artifacts(
            remote_name=remote_name,
            name=name,
            project=project,
        )

        if not matches:
            console.print(f"[error]{exc}[/error]")
            raise typer.Exit(1) from None

        console.print(f"[error]{exc}[/error]\n")

        names = sorted({artifact.name for artifact in matches})

        selected_name = select(
            "Select a matching artifact:",
            [
                questionary.Choice(
                    title=candidate,
                    value=candidate,
                )
                for candidate in names
            ],
        )

        if selected_name is None:
            raise typer.Exit() from None

        return resolve_remote_artifact_or_exit(
            console=console,
            remote_name=remote_name,
            name=cast(str, selected_name),
            project=project,
            version=version,
        )

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

        selected = select(
            "Select version:",
            [
                questionary.Choice(
                    title=artifact.version,
                    value=artifact,
                )
                for artifact in artifacts
            ],
        )

        if selected is None:
            raise typer.Exit() from None

        return cast(RemoteArtifact, selected)


def resolve_checkpoint_role(
    artifact: Artifact,
    role: str | None,
) -> str:
    roles = artifact.checkpoint_roles()

    if not roles:
        raise typer.BadParameter(f"Artifact '{artifact.name}' contains no checkpoints.")

    if role is not None:
        if role not in roles:
            raise typer.BadParameter(
                f"Checkpoint role '{role}' not found. Available roles: {', '.join(roles)}"
            )

        return role

    if len(roles) == 1:
        return roles[0]

    selected = select(
        "Select checkpoint:",
        [
            questionary.Choice(
                title=candidate,
                value=candidate,
            )
            for candidate in roles
        ],
    )

    return cast(str, selected)
