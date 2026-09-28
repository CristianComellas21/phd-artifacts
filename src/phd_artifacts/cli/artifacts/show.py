import typer
from rich.console import Console
from rich.table import Table

from phd_artifacts.artifacts import discover_artifacts

console = Console()


def show_artifact(
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
    """Show information about a promoted artifact."""

    artifacts = [artifact for artifact in discover_artifacts(project) if artifact.name == name]

    if version is not None:
        artifacts = [artifact for artifact in artifacts if artifact.version == version]

    if not artifacts:
        console.print(f"[red]Artifact '{name}' not found.[/red]")
        raise typer.Exit(1)

    if len(artifacts) > 1:
        console.print(f"[yellow]Multiple versions found for '{name}'.[/yellow]")

        table = Table("Version", "Project", "Promoted")

        for artifact in artifacts:
            table.add_row(
                artifact.version,
                artifact.project,
                artifact.metadata.get("promoted_at", "-"),
            )

        console.print(table)

        console.print("\nSpecify one with [bold]--version[/bold].")
        raise typer.Exit(1)

    artifact = artifacts[0]
    metadata = artifact.metadata

    console.print(f"[bold]{artifact.name}[/bold]\n")

    console.print(f"Project:     {artifact.project}")
    console.print(f"Type:        {artifact.artifact_type}")
    console.print(f"Version:     {artifact.version}")
    console.print(f"Experiment:  {metadata.get('experiment', '-')}")
    console.print(f"Model:       {metadata.get('model', '-')}")
    console.print(f"Run:         {metadata.get('run_id', '-')}")
    console.print(f"Host:        {metadata.get('source_host', '-')}")
    console.print(f"Promoted:    {metadata.get('promoted_at', '-')}")
    console.print(f"Path:        {artifact.path}")

    artifact_info = metadata.get("artifact", {})

    size_bytes = artifact_info.get("size_bytes")

    if size_bytes is not None:
        console.print(f"Size:        {size_bytes / (1024**2):.1f} MB")

    checksum = artifact_info.get("sha256")

    if checksum:
        console.print(f"SHA256:      {checksum}")
