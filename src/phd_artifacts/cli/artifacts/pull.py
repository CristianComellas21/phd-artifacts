import typer

from phd_artifacts.artifacts import pull_artifact
from phd_artifacts.artifacts.exceptions import LocalArtifactConflictError
from phd_artifacts.artifacts.transfer import PullAction
from phd_artifacts.cli.artifacts.common import resolve_remote_artifact_or_exit
from phd_artifacts.cli.ui import console


def pull(
    name: str = typer.Argument(
        ...,
        help="Artifact name.",
    ),
    remote: str = typer.Option(
        ...,
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

    artifact = resolve_remote_artifact_or_exit(
        console=console,
        remote_name=remote,
        name=name,
        project=project,
        version=version,
    )

    try:
        result = pull_artifact(
            artifact=artifact,
            force=force,
        )

    except LocalArtifactConflictError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None

    if result.action is PullAction.ALREADY_UP_TO_DATE:
        console.print("[green]Artifact is already up to date.[/green]")

    elif result.action is PullAction.OVERWRITTEN:
        console.print("[yellow]Artifact overwritten from remote.[/yellow]")

    else:
        console.print("[green]Artifact downloaded successfully.[/green]")

    console.print(f"Remote:   {artifact.remote}")
    console.print(f"Artifact: {artifact.name}")
    console.print(f"Version:  {artifact.version}")
    console.print(f"Path:     {result.destination}")
