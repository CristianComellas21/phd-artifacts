import shlex
from dataclasses import dataclass
from pathlib import Path

from phd_artifacts.cli.ui import text
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
        root = Path(text("Project root")).expanduser().resolve()

        default_logs = root / "logs"
        default_artifacts = root / "artifacts"

        logs = (
            Path(
                text(
                    "Logs directory",
                    default=str(default_logs),
                )
            )
            .expanduser()
            .resolve()
        )

        workspace_artifacts = (
            Path(
                text(
                    "Workspace artifacts directory",
                    default=str(default_artifacts),
                )
            )
            .expanduser()
            .resolve()
        )

        python_raw = text("Python executable [optional]", default="")

        exporter = text("Portable exporter [optional]", default="")

        exporter_args_raw = text("Exporter arguments [optional]", default="")

    else:
        root = (
            Path(
                text(
                    "Project root",
                    default=existing["root"],
                )
            )
            .expanduser()
            .resolve()
        )

        logs = (
            Path(
                text(
                    "Logs directory",
                    default=existing["logs"],
                )
            )
            .expanduser()
            .resolve()
        )

        workspace_artifacts = (
            Path(
                text(
                    "Workspace artifacts directory",
                    default=existing["workspace_artifacts"],
                )
            )
            .expanduser()
            .resolve()
        )

        python_raw = text("Python executable", default=existing.get("python", ""))

        exporter = text("Portable exporter", default=existing.get("exporter", ""))

        existing_args = existing.get(
            "exporter_args",
            [],
        )

        exporter_args_raw = text("Exporter arguments", default=shlex.join(existing_args))

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
