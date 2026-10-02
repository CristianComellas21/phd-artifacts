import typer
from rich.console import Console
from rich.table import Table

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
        result = verify_artifact(artifact)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from None

    console.print(f"[bold]{artifact.name}[/bold]")
    console.print(f"Version: {artifact.version}")

    table = Table(
        "File",
        "Exists",
        "Size",
        "SHA256",
    )

    for file_result in result.files:
        table.add_row(
            file_result.path,
            "[green]yes[/green]" if file_result.exists else "[red]no[/red]",
            "[green]OK[/green]" if file_result.size_ok else "[red]FAILED[/red]",
            "[green]OK[/green]" if file_result.sha256_ok else "[red]FAILED[/red]",
        )

    console.print(table)

    if result.ok:
        console.print("[green]Status: OK[/green]")
        return

    console.print("[red]Status: FAILED[/red]")
    raise typer.Exit(1)
