import typer
from rich.console import Console

from phd_artifacts.cli.artifacts.common import resolve_artifact_or_exit
from phd_artifacts.core.display import print_yaml_file

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
    show_config: bool = typer.Option(
        False,
        "--config",
        help="Show the stored Hydra configuration.",
    ),
    show_overrides: bool = typer.Option(
        False,
        "--overrides",
        help="Show the stored Hydra overrides.",
    ),
    show_full: bool = typer.Option(
        False,
        "--full",
        help="Show configuration and overrides.",
    ),
):
    """Show information about a promoted artifact."""

    artifact = resolve_artifact_or_exit(
        console=console,
        name=name,
        version=version,
        project=project,
    )

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

    if show_config or show_full:
        print_yaml_file(
            console,
            artifact.path / "config.yaml",
            "Configuration",
        )

    if show_overrides or show_full:
        print_yaml_file(
            console,
            artifact.path / "overrides.yaml",
            "Overrides",
        )
