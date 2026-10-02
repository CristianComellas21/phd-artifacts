import shlex
from dataclasses import dataclass
from pathlib import Path

import typer

from phd_artifacts.projects.models import ProjectConfig


@dataclass
class ProjectInput:
    root: Path
    logs: Path
    workspace_artifacts: Path
    python: Path | None
    exporter: str | None
    exporter_args: list[str] | None


def prompt_project_config(
    existing: ProjectConfig | None = None,
) -> ProjectInput:
    """Interactively collect project configuration."""

    if existing is None:
        root = Path(typer.prompt("Project root")).expanduser().resolve()

        default_logs = root / "logs"
        default_artifacts = root / "artifacts"

        logs = (
            Path(
                typer.prompt(
                    "Logs directory",
                    default=str(default_logs),
                )
            )
            .expanduser()
            .resolve()
        )

        workspace_artifacts = (
            Path(
                typer.prompt(
                    "Workspace artifacts directory",
                    default=str(default_artifacts),
                )
            )
            .expanduser()
            .resolve()
        )

        python_raw = typer.prompt(
            "Python executable [optional]",
            default="",
            show_default=False,
        )

        exporter = typer.prompt(
            "Portable exporter [optional]",
            default="",
            show_default=False,
        )

        exporter_args_raw = typer.prompt(
            "Exporter arguments [optional]",
            default="",
            show_default=False,
        )

    else:
        root = (
            Path(
                typer.prompt(
                    "Project root",
                    default=existing["root"],
                )
            )
            .expanduser()
            .resolve()
        )

        logs = (
            Path(
                typer.prompt(
                    "Logs directory",
                    default=existing["logs"],
                )
            )
            .expanduser()
            .resolve()
        )

        workspace_artifacts = (
            Path(
                typer.prompt(
                    "Workspace artifacts directory",
                    default=existing["workspace_artifacts"],
                )
            )
            .expanduser()
            .resolve()
        )

        python_raw = typer.prompt(
            "Python executable",
            default=existing.get("python", ""),
            show_default=bool(existing.get("python")),
        )

        exporter = typer.prompt(
            "Portable exporter",
            default=existing.get("exporter", ""),
            show_default=bool(existing.get("exporter")),
        )

        existing_args = existing.get(
            "exporter_args",
            [],
        )

        exporter_args_raw = typer.prompt(
            "Exporter arguments",
            default=shlex.join(existing_args),
            show_default=bool(existing_args),
        )

    python = Path(python_raw).expanduser().resolve() if python_raw else None

    exporter = exporter or None

    exporter_args = shlex.split(exporter_args_raw) if exporter_args_raw else None

    return ProjectInput(
        root=root,
        logs=logs,
        workspace_artifacts=workspace_artifacts,
        python=python,
        exporter=exporter,
        exporter_args=exporter_args,
    )
