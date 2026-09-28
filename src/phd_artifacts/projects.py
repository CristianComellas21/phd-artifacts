from pathlib import Path

from phd_artifacts.config import load_config, save_config


def add_project(
    name: str,
    root: Path,
    logs: Path | None = None,
    workspace_artifacts: Path | None = None,
) -> dict:
    """Register a new research project."""

    config = load_config()
    projects = config.setdefault("projects", {})

    if name in projects:
        raise ValueError(f"Project '{name}' already exists.")

    root = root.expanduser().resolve()

    if not root.exists():
        raise FileNotFoundError(f"Project root does not exist: {root}")

    logs = (
        logs.expanduser().resolve()
        if logs is not None
        else root / "logs"
    )

    workspace_artifacts = (
        workspace_artifacts.expanduser().resolve()
        if workspace_artifacts is not None
        else root / "artifacts"
    )

    project = {
        "root": str(root),
        "logs": str(logs),
        "workspace_artifacts": str(workspace_artifacts),
    }

    projects[name] = project
    save_config(config)

    return project


def remove_project(name: str) -> None:
    """Remove a registered project."""

    config = load_config()
    projects = config.get("projects", {})

    if name not in projects:
        raise KeyError(name)

    del projects[name]
    save_config(config)


def list_projects() -> dict:
    """Return all registered projects."""

    config = load_config()
    return config.get("projects", {})


def get_project(name: str) -> dict:
    """Return a project by name."""

    projects = list_projects()

    if name not in projects:
        raise KeyError(name)

    return projects[name]


def get_current_project(
    path: Path | None = None,
) -> tuple[str, dict] | None:
    """Find the registered project containing the given path."""

    current_path = (
        path.expanduser().resolve()
        if path is not None
        else Path.cwd().resolve()
    )

    matches: list[tuple[str, dict, Path]] = []

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