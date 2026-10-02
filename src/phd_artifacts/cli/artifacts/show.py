import typer
from rich.console import Console
from rich.table import Table

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

    console.print(f"Project:    {artifact.project}")
    console.print(f"Type:       {artifact.artifact_type}")
    console.print(f"Version:    {artifact.version}")
    console.print(f"Experiment: {metadata.get('experiment', '-')}")
    console.print(f"Model:      {metadata.get('model', '-')}")
    console.print(f"Run:        {metadata.get('run_id', '-')}")
    console.print(f"Host:       {metadata.get('source_host', '-')}")
    console.print(f"Promoted:   {metadata.get('promoted_at', '-')}")
    console.print(f"Path:       {artifact.path}")

    checkpoints = metadata.get("checkpoints", {})

    if checkpoints:
        console.print("\n[bold]Checkpoints[/bold]")

        table = Table(
            "Role",
            "File",
            "Size",
            "Portable",
        )

        for role, checkpoint in checkpoints.items():
            size_bytes = checkpoint.get("size_bytes", 0)
            portable_files = checkpoint.get(
                "portable_files",
                [],
            )

            table.add_row(
                role,
                checkpoint.get("path", "-"),
                f"{size_bytes / (1024**2):.1f} MB",
                str(len(portable_files)),
            )

        console.print(table)

    exporter = metadata.get("export", {}).get("exporter")

    if exporter:
        console.print(f"\nExporter: {exporter}")

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
