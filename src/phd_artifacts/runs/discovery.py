import hashlib
from datetime import datetime
from pathlib import Path

from phd_artifacts.runs.models import Run


def _make_run_id(relative_path: Path) -> str:
    """Generate a stable short ID from the run path."""

    return hashlib.sha1(str(relative_path).encode("utf-8")).hexdigest()[:8]


def _parse_run_path(
    relative_path: Path,
) -> tuple[str | None, str | None, datetime | None]:
    """
    Try to identify a Hydra run path containing:

        .../<experiment>/<model>/<YYYY-MM-DD>/<HH-MM-SS>/...

    The date/time pair is detected instead of assuming a fixed path depth.
    """

    parts = relative_path.parts

    for i in range(1, len(parts)):
        try:
            created_at = datetime.strptime(
                f"{parts[i - 1]} {parts[i]}",
                "%Y-%m-%d %H-%M-%S",
            )
        except ValueError:
            continue

        model_index = i - 2
        experiment_index = i - 3

        model = parts[model_index] if model_index >= 0 else None

        experiment = parts[experiment_index] if experiment_index >= 0 else None

        return experiment, model, created_at

    return None, None, None


def discover_runs(
    logs_path: Path,
    project_name: str,
    include_tests: bool = False,
) -> list[Run]:
    """Discover Hydra runs inside a logs directory."""

    logs_path = logs_path.expanduser().resolve()

    if not logs_path.exists():
        return []

    runs: list[Run] = []

    for hydra_dir in logs_path.rglob(".hydra"):
        if not hydra_dir.is_dir():
            continue

        run_path = hydra_dir.parent
        relative_path = run_path.relative_to(logs_path)

        if not include_tests and relative_path.parts:
            if relative_path.parts[0] == "test":
                continue

        experiment, model, created_at = _parse_run_path(relative_path)

        runs.append(
            Run(
                id=_make_run_id(relative_path),
                project=project_name,
                path=run_path,
                relative_path=relative_path,
                experiment=experiment,
                model=model,
                created_at=created_at,
                modified_at=datetime.fromtimestamp(run_path.stat().st_mtime),
                has_checkpoints=(run_path / "checkpoints").is_dir(),
            )
        )

    runs.sort(
        key=lambda run: run.created_at or run.modified_at,
        reverse=True,
    )

    return runs


def get_run_checkpoints(run: Run) -> list[Path]:
    """Return checkpoint files contained in a run."""

    checkpoint_dir = run.path / "checkpoints"

    if not checkpoint_dir.is_dir():
        return []

    return sorted(
        (
            path
            for path in checkpoint_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in {".ckpt", ".pth", ".pt"}
        ),
        key=lambda path: path.name,
    )
