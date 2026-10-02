import os
from pathlib import Path
from typing import cast

from phd_artifacts.core.config import load_config, save_config
from phd_artifacts.projects.exceptions import (
    ProjectNotFoundError,
    ProjectNotResolvedError,
)
from phd_artifacts.projects.models import ProjectConfig


def add_project(
    name: str,
    root: Path,
    logs: Path | None = None,
    workspace_artifacts: Path | None = None,
    python: Path | None = None,
    exporter: str | None = None,
    exporter_args: list[str] | None = None,
) -> ProjectConfig:
    """Register a new research project."""

    config = load_config()

    projects = cast(
        dict[str, ProjectConfig],
        config.setdefault("projects", {}),
    )

    if name in projects:
        raise ValueError(f"Project '{name}' already exists.")

    root = root.expanduser().resolve()

    if not root.exists():
        raise FileNotFoundError(f"Project root does not exist: {root}")

    logs = logs.expanduser().resolve() if logs is not None else root / "logs"

    workspace_artifacts = (
        workspace_artifacts.expanduser().resolve()
        if workspace_artifacts is not None
        else root / "artifacts"
    )

    project: ProjectConfig = {
        "root": str(root),
        "logs": str(logs),
        "workspace_artifacts": str(workspace_artifacts),
    }

    if python is not None:
        python = python.expanduser().resolve()

        if not python.is_file():
            raise FileNotFoundError(f"Python executable not found: {python}")

        if not os.access(python, os.X_OK):
            raise ValueError(f"Python is not executable: {python}")

        project["python"] = str(python)

    if exporter is not None:
        exporter_path = root / exporter

        if not exporter_path.is_file():
            raise FileNotFoundError(f"Exporter not found: {exporter_path}")

        project["exporter"] = exporter

    if exporter_args:
        project["exporter_args"] = exporter_args

    projects[name] = project

    save_config(config)

    return project


def remove_project(name: str) -> None:
    """Remove a registered project."""

    config = load_config()
    projects = config.get("projects", {})

    if name not in projects:
        raise ProjectNotFoundError(name)

    del projects[name]
    save_config(config)


def list_projects() -> dict[str, ProjectConfig]:
    """Return all registered projects."""

    config = load_config()
    return config.get("projects", {})


def get_project(name: str) -> ProjectConfig:
    """Return a project by name."""

    projects = list_projects()

    if name not in projects:
        raise ProjectNotFoundError(name)

    return projects[name]


def resolve_project(
    project_name: str | None = None,
) -> tuple[str, ProjectConfig]:
    """Resolve a project name and its configuration."""

    if project_name is not None:
        return project_name, get_project(project_name)

    current = get_current_project()

    if current is None:
        raise ProjectNotResolvedError()

    return current


def get_current_project(
    path: Path | None = None,
) -> tuple[str, ProjectConfig] | None:
    """Find the registered project containing the given path."""

    current_path = path.expanduser().resolve() if path is not None else Path.cwd().resolve()

    matches: list[tuple[str, ProjectConfig, Path]] = []

    for name, project in list_projects().items():
        root = Path(project["root"]).resolve()

        if current_path == root or current_path.is_relative_to(root):
            matches.append((name, project, root))

    if not matches:
        return None

    # Prefer the most specific project when roots are nested.
    matches.sort(
        key=lambda item: len(item[2].parts),
        reverse=True,
    )

    name, project, _ = matches[0]

    return name, project
