import typer

from phd_artifacts.artifacts.transfer import (
    get_artifact_remote_status,
)
from phd_artifacts.cli.artifacts.common import (
    resolve_artifact_or_exit,
)
from phd_artifacts.cli.remotes.common import resolve_remote_name
from phd_artifacts.cli.ui import activity, console
from phd_artifacts.remotes.exceptions import RemoteError
from phd_artifacts.remotes.status import RemoteStatus


def status(
    name: str = typer.Argument(
        ...,
        help="Artifact name.",
    ),
    remote: str = typer.Option(
        None,
        "--remote",
        "-r",
        help="Remote to check.",
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
    """Show the remote status of a promoted artifact."""

    artifact = resolve_artifact_or_exit(
        console=console,
        name=name,
        version=version,
        project=project,
    )

    remote_name = resolve_remote_name(remote)
    try:
        with activity(f"Comparing artifact with '{remote_name}'"):
            comparison = get_artifact_remote_status(
                artifact,
                remote_name=remote_name,
            )
    except (RemoteError, RuntimeError) as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None

    console.print(f"[accent]{artifact.name}[/accent]\n")
    console.print(f"Project:  {artifact.project}")
    console.print(f"Version:  {artifact.version}")
    console.print(f"Remote:   {remote_name}")

    match comparison.status:
        case RemoteStatus.UP_TO_DATE:
            console.print("Status:   [success]up to date[/success]")

        case RemoteStatus.MISSING:
            console.print("Status:   [warning]missing[/warning]")

        case RemoteStatus.DIFFERENT:
            console.print("Status:   [error]different[/error]")
