import typer

from phd_artifacts.artifacts import remove_artifact
from phd_artifacts.artifacts.exceptions import RemoteIndexError
from phd_artifacts.artifacts.remove import (
    finalize_remote_removal,
    perform_remote_removal,
    prepare_remote_removal,
)
from phd_artifacts.cli.artifacts.common import (
    resolve_artifact_or_exit,
    resolve_remote_artifact_or_exit,
)
from phd_artifacts.cli.remotes.common import resolve_remote_name
from phd_artifacts.cli.ui import activity, confirm, console


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
    """Remove a promoted artifact locally or from a remote."""

    if remote is None:
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

    artifact = resolve_remote_artifact_or_exit(
        console=console,
        remote_name=remote_name,
        name=name,
        version=version,
        project=project,
    )

    if not yes:
        confirmed = confirm(
            f"Remove artifact '{artifact.name}' version "
            f"'{artifact.version}' from remote '{remote_name}'?",
            default=False,
        )

        if not confirmed:
            raise typer.Exit(0)

    prepared = prepare_remote_removal(artifact)

    with activity("Removing remote artifact"):
        perform_remote_removal(prepared)

    try:
        with activity("Updating remote index"):
            finalize_remote_removal(prepared)

    except RemoteIndexError as exc:
        console.print(
            "[warning]Artifact was removed successfully, "
            "but the remote index could not be updated.[/warning]"
        )
        console.print(f"[muted]Remote index operation failed: {exc.operation}[/muted]")
        console.print(
            f"[muted]Run 'phd-artifact remote rebuild-index "
            f"{exc.remote_name}' to repair it.[/muted]"
        )

    console.print(
        f"[success]Removed artifact '{artifact.name}' version "
        f"'{artifact.version}' from '{remote_name}'.[/success]"
    )
