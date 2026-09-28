import typer
from rich.console import Console

from phd_artifacts.artifacts import discover_artifacts, verify_artifact

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

    artifacts = [artifact for artifact in discover_artifacts(project) if artifact.name == name]

    if version is not None:
        artifacts = [artifact for artifact in artifacts if artifact.version == version]

    if not artifacts:
        console.print(f"[red]Artifact '{name}' not found.[/red]")
        raise typer.Exit(1)

    if len(artifacts) > 1:
        console.print(
            f"[yellow]Multiple versions found for '{name}'. Specify one with --version.[/yellow]"
        )
        raise typer.Exit(1)

    artifact = artifacts[0]

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
