import typer
from rich.table import Table

from phd_artifacts.artifacts import verify_artifact
from phd_artifacts.cli.artifacts.common import resolve_artifact_or_exit
from phd_artifacts.cli.ui import console


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
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None

    console.print(f"[accent]{artifact.name}[/accent]")
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
            "[success]yes[/success]" if file_result.exists else "[error]no[/error]",
            "[success]OK[/success]" if file_result.size_ok else "[error]FAILED[/error]",
            "[success]OK[/success]" if file_result.sha256_ok else "[error]FAILED[/error]",
        )

    console.print(table)

    if result.ok:
        console.print("[success]Status: OK[/success]")
        return

    console.print("[error]Status: FAILED[/error]")
    raise typer.Exit(1)
