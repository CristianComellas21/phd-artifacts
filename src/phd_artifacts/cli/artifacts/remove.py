from typing import cast

import questionary
import typer

from phd_artifacts.artifacts import remove_artifact
from phd_artifacts.artifacts.exceptions import RemoteIndexError
from phd_artifacts.artifacts.models import RemoteArtifact
from phd_artifacts.artifacts.queries import get_remote_artifacts
from phd_artifacts.artifacts.remote_index import remove_remote_index_entries
from phd_artifacts.artifacts.remove import (
    perform_remote_removal,
    prepare_remote_removal,
)
from phd_artifacts.artifacts.status import get_remote_artifact_local_states
from phd_artifacts.cli.artifacts.common import (
    resolve_artifact_or_exit,
    resolve_remote_artifact_or_exit,
)
from phd_artifacts.cli.remotes.common import resolve_remote_name
from phd_artifacts.cli.ui import activity, checkbox, confirm, console
from phd_artifacts.remotes.status import RemoteStatus


def _format_status(status: RemoteStatus) -> str:
    if status is RemoteStatus.MISSING:
        return "remote only"

    if status is RemoteStatus.UP_TO_DATE:
        return "up to date"

    if status is RemoteStatus.DIFFERENT:
        return "different"

    return status.value


def remove(
    name: str | None = typer.Argument(
        None,
        help="Artifact name.",
    ),
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
    remote: str | None = typer.Option(
        None,
        "--remote",
        "-r",
        help="Remove the artifact from a remote instead of locally.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Remove without confirmation.",
    ),
):
    """Remove promoted artifacts locally or from a remote."""

    if remote is None:
        if name is None:
            console.print("[error]Artifact name is required for local removal.[/error]")
            raise typer.Exit(1)

        artifact = resolve_artifact_or_exit(
            console=console,
            name=name,
            version=version,
            project=project,
        )

        if not yes:
            confirmed = confirm(
                f"Remove local artifact '{artifact.name}' version '{artifact.version}'?",
                default=False,
            )

            if not confirmed:
                raise typer.Exit(0)

        remove_artifact(artifact)

        console.print(
            f"[success]Removed artifact '{artifact.name}' version '{artifact.version}'.[/success]"
        )
        return

    remote_name = resolve_remote_name(remote)

    if name is not None:
        artifact = resolve_remote_artifact_or_exit(
            console=console,
            remote_name=remote_name,
            name=name,
            version=version,
            project=project,
        )

        artifacts = [artifact]

    else:
        if version is not None:
            console.print("[error]--version requires an artifact name.[/error]")
            raise typer.Exit(1)

        with activity(f"Loading artifacts from '{remote_name}'"):
            remote_artifacts = get_remote_artifacts(
                remote_name=remote_name,
                project=project,
            )

        with activity("Comparing remote and local artifacts") as reporter:
            states = get_remote_artifact_local_states(
                artifacts=remote_artifacts,
                progress=reporter,
            )

        states.sort(
            key=lambda state: (
                state.status is not RemoteStatus.MISSING,
                state.artifact.name.lower(),
            )
        )

        if not remote_artifacts:
            console.print(f"[info]No artifacts found on remote '{remote_name}'.[/info]")
            raise typer.Exit(0)

        selected = checkbox(
            "Select artifacts to remove:",
            choices=[
                questionary.Choice(
                    title=(
                        f"{state.artifact.name}[{state.artifact.version}] [{_format_status(state.status)}]"
                    ),
                    value=state.artifact,
                )
                for state in states
            ],
        )

        artifacts = cast(list[RemoteArtifact], selected)

        if not artifacts:
            raise typer.Exit(0)

    if not yes:
        if len(artifacts) == 1:
            artifact = artifacts[0]

            message = (
                f"Remove artifact '{artifact.name}' version "
                f"'{artifact.version}' from remote '{remote_name}'?"
            )
        else:
            message = f"Remove {len(artifacts)} artifacts from remote '{remote_name}'?"

        if not confirm(message, default=False):
            raise typer.Exit(0)

    removed: list[RemoteArtifact] = []
    failed: list[tuple[RemoteArtifact, Exception]] = []

    for artifact in artifacts:
        prepared = prepare_remote_removal(artifact)

        try:
            with activity(f"Removing '{artifact.name}'"):
                perform_remote_removal(prepared)

        except Exception as exc:
            failed.append((artifact, exc))
            continue

        removed.append(artifact)

    index_error: RemoteIndexError | None = None

    if removed:
        try:
            with activity("Updating remote index"):
                remove_remote_index_entries(
                    remote_name=remote_name,
                    artifact_paths=[artifact.path for artifact in removed],
                )

        except RemoteIndexError as exc:
            index_error = exc

    if len(removed) == 1:
        artifact = removed[0]

        console.print(
            f"[success]Removed artifact '{artifact.name}' version "
            f"'{artifact.version}' from '{remote_name}'.[/success]"
        )

    elif removed:
        console.print(f"[success]Removed {len(removed)} artifacts from '{remote_name}'.[/success]")

    if failed:
        console.print(f"[warning]Failed to remove {len(failed)} artifact(s):[/warning]")

        for artifact, exc in failed:
            console.print(f"[error]- {artifact.name} [{artifact.version}]: {exc}[/error]")

    if index_error is not None:
        console.print(
            "[warning]The remote artifacts were removed, "
            "but the remote index could not be updated.[/warning]"
        )
        console.print(
            f"[muted]Run 'phd-artifact remote rebuild-index "
            f"{index_error.remote_name}' to repair it.[/muted]"
        )
