from pathlib import Path

import typer

from phd_artifacts.cli.projects.common import prompt_project_config
from phd_artifacts.cli.ui import confirm, console, text
from phd_artifacts.core.config import (
    config_exists,
    create_config,
    get_config_path,
)
from phd_artifacts.projects.service import add_project


def init(
    artifact_root: Path | None = typer.Option(
        None,
        "--artifact-root",
        "-r",
        help="Root directory for promoted research artifacts.",
    ),
):
    """Initialize phd-artifacts on this machine."""

    config_path = get_config_path()

    if config_exists():
        overwrite = confirm(f"Configuration already exists at {config_path}. Overwrite it?")

        if not overwrite:
            raise typer.Exit()

    if artifact_root is None:
        artifact_root = Path(
            text(
                "Artifact store",
                default="~/phd/artifact-store",
            )
        )

    artifact_root = artifact_root.expanduser().resolve()

    artifact_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    create_config(artifact_root)

    console.print("\n[success]Configuration created successfully.[/success]")
    console.print(f"Config:    {config_path}")
    console.print(f"Artifacts: {artifact_root}")

    if not typer.confirm(
        "\nRegister a project now?",
        default=True,
    ):
        return

    name = text("Project name").strip()

    values = prompt_project_config()

    project = add_project(
        name=name,
        root=values.root,
        logs=values.logs,
        workspace_artifacts=values.workspace_artifacts,
        python=values.python,
        exporter=values.exporter,
        exporter_args=values.exporter_args,
    )

    console.print(f"\n[success]Project '{name}' registered.[/success]")
    console.print(f"Root:     {project['root']}")
