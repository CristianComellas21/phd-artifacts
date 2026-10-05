import typer
from rich.table import Table

from phd_artifacts.artifacts.queries import get_artifacts
from phd_artifacts.artifacts.status import get_artifact_remote_states
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


def _format_status(status: RemoteStatus) -> str:
    match status:
        case RemoteStatus.UP_TO_DATE:
            return "[success]up to date[/success]"
        case RemoteStatus.MISSING:
            return "[warning]missing[/warning]"
        case RemoteStatus.DIFFERENT:
            return "[error]different[/error]"


def status(
    name: str | None = typer.Argument(
        None,
        help="Artifact name. Omit to show all artifacts.",
    ),
    remote: str | None = typer.Option(
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
    """Show the remote status of promoted artifacts."""

    if name is None and version is not None:
        raise typer.BadParameter("--version requires an artifact name.")

    remote_name = resolve_remote_name(remote)

    if name is not None:
        artifact = resolve_artifact_or_exit(
            console=console,
            name=name,
            version=version,
            project=project,
        )

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
        console.print(f"Status:   {_format_status(comparison.status)}")

        return

    artifacts = get_artifacts(
        project=project,
    )

    if not artifacts:
        console.print("[warning]No local artifacts found.[/warning]")
        raise typer.Exit(0)

    try:
        with activity(f"Checking artifacts against '{remote_name}'") as reporter:
            states = get_artifact_remote_states(
                artifacts=artifacts,
                remote_name=remote_name,
                progress=reporter,
            )
    except (RemoteError, RuntimeError) as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None

    table = Table(
        "Project",
        "Name",
        "Version",
        "Remote",
        "Status",
    )

    for state in states:
        status_text = _format_status(state.status)

        table.add_row(
            state.artifact.project,
            state.artifact.name,
            state.artifact.version,
            remote_name,
            status_text,
        )

    console.print(table)
