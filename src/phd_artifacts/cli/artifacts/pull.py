import typer

from phd_artifacts.artifacts.exceptions import LocalArtifactConflictError
from phd_artifacts.artifacts.models import RemoteArtifact
from phd_artifacts.artifacts.transfer import (
    PullAction,
    PullResult,
    perform_pull,
    prepare_pull,
    verify_pulled_artifact,
)
from phd_artifacts.cli.artifacts.common import resolve_remote_artifact_or_exit
from phd_artifacts.cli.remotes.common import resolve_remote_name
from phd_artifacts.cli.ui import activity, confirm, console


def _pull_artifact(
    artifact: RemoteArtifact,
    force: bool,
) -> PullResult:
    """Pull a promoted artifact from a configured remote."""

    def prepare(force_value: bool):
        with activity("Preparing download") as reporter:
            return prepare_pull(
                artifact=artifact,
                force=force_value,
                progress=reporter,
            )

    try:
        try:
            prepared = prepare(force)

        except LocalArtifactConflictError:
            if not confirm(
                f"Local artifact '{artifact.name}' differs. Overwrite local copy?",
                default=False,
            ):
                raise typer.Exit(0) from None

            prepared = prepare(True)

        result = perform_pull(prepared)

        if result.action is not PullAction.ALREADY_UP_TO_DATE:
            with activity("Verifying download") as reporter:
                verify_pulled_artifact(
                    prepared,
                    progress=reporter,
                )

        return result

    except RuntimeError as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None


def pull(
    name: str = typer.Argument(
        ...,
        help="Artifact name.",
    ),
    remote: str | None = typer.Option(
        None,
        "--remote",
        "-r",
        help="Remote name.",
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
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite a different local artifact.",
    ),
):
    """Pull a promoted artifact from a configured remote."""

    remote_name = resolve_remote_name(remote)

    artifact = resolve_remote_artifact_or_exit(
        console=console,
        remote_name=remote_name,
        name=name,
        project=project,
        version=version,
    )

    result = _pull_artifact(
        artifact=artifact,
        force=force,
    )

    match result.action:
        case PullAction.ALREADY_UP_TO_DATE:
            console.print("[success]Artifact is already up to date.[/success]")

        case PullAction.OVERWRITTEN:
            console.print("[warning]Artifact overwritten from remote.[/warning]")

        case PullAction.DOWNLOADED:
            console.print("[success]Artifact downloaded successfully.[/success]")

    console.print(f"Remote:   {artifact.remote}")
    console.print(f"Artifact: {artifact.name}")
    console.print(f"Version:  {artifact.version}")
    console.print(f"Path:     {result.destination}")
