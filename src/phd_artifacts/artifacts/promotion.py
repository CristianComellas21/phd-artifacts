import platform
import shutil
from datetime import UTC, datetime
from pathlib import Path

import tomli_w

from phd_artifacts.artifacts.export import export_portable_weights
from phd_artifacts.artifacts.verification import compute_sha256
from phd_artifacts.core.config import load_config
from phd_artifacts.projects.service import get_project
from phd_artifacts.runs.models import Run


def get_checkpoint_store(project_name: str) -> Path:
    config = load_config()

    artifact_root = Path(config["artifact_root"])

    return artifact_root / project_name / "checkpoints"


def get_artifact_version(run: Run) -> str:
    timestamp = run.created_at or run.modified_at

    return f"{timestamp:%Y%m%d_%H%M%S}_{run.id}"


def promote_checkpoint(
    run: Run,
    checkpoint: Path,
    name: str,
    no_export: bool = False,
) -> Path:
    """Promote a run checkpoint into the persistent artifact store."""

    project_name = run.project
    project_config = get_project(project_name)

    store = get_checkpoint_store(project_name)
    version = get_artifact_version(run)

    destination = store / name / version

    if destination.exists():
        raise FileExistsError(f"Artifact already exists: {destination}")

    destination.mkdir(parents=True)

    try:
        checkpoint_destination = destination / "training.ckpt"

        shutil.copy2(
            checkpoint,
            checkpoint_destination,
        )

        hydra_dir = run.path / ".hydra"

        for filename in (
            "config.yaml",
            "overrides.yaml",
            "hydra.yaml",
        ):
            source = hydra_dir / filename

            if source.is_file():
                shutil.copy2(
                    source,
                    destination / filename,
                )

        export_result = None

        if not no_export:
            export_result = export_portable_weights(
                checkpoint_path=checkpoint_destination,
                artifact_path=destination,
                project_config=project_config,
            )

        metadata = {
            "version": 1,
            "name": name,
            "project": project_name,
            "type": "checkpoint",
            "run_id": run.id,
            "experiment": run.experiment or "",
            "model": run.model or "",
            "source_host": platform.node(),
            "promoted_at": datetime.now(UTC).isoformat(),
            "source": {
                "run": str(run.path),
                "checkpoint": str(checkpoint),
            },
            "artifact": {
                "checkpoint": "training.ckpt",
                "size_bytes": (checkpoint_destination.stat().st_size),
                "sha256": compute_sha256(checkpoint_destination),
            },
        }

        if run.created_at:
            metadata["run_created_at"] = run.created_at.isoformat()

        if export_result is not None:
            portable_files = []

            for path in export_result.files:
                portable_files.append(
                    {
                        "path": path.relative_to(destination).as_posix(),
                        "size_bytes": path.stat().st_size,
                        "sha256": compute_sha256(path),
                    }
                )

            metadata["export"] = {
                "status": "ok",
                "exporter": project_config["exporter"],
            }

            metadata["portable_files"] = portable_files

        with (destination / "metadata.toml").open("wb") as file:
            tomli_w.dump(
                metadata,
                file,
            )

    except Exception:
        shutil.rmtree(
            destination,
            ignore_errors=True,
        )
        raise

    return destination
