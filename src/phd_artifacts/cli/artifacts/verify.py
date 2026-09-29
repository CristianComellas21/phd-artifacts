import typer
from rich.console import Console

from phd_artifacts.artifacts import verify_artifact
from phd_artifacts.cli.artifacts.common import resolve_artifact_or_exit

console = Console()


def verify(
    name: str = typer.Argument(
        ...,
        help="Artifact name.",
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
    """Verify the integrity of a promoted artifact."""

    artifact = resolve_artifact_or_exit(
        console=console,
        name=name,
        version=version,
        project=project,
    )

    try:
        valid, expected, actual = verify_artifact(artifact)
    except (ValueError, FileNotFoundError) as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None

    console.print(f"[bold]{artifact.name}[/bold]")
    console.print(f"Version:   {artifact.version}")
    console.print(f"Expected:  {expected}")
    console.print(f"Actual:    {actual}")

    if valid:
        console.print("[green]Status:    OK[/green]")
        return

    console.print("[red]Status:    FAILED[/red]")
    raise typer.Exit(1)
