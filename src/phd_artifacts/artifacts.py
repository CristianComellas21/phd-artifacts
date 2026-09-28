import hashlib
import platform
import shutil
from datetime import UTC, datetime
from pathlib import Path

import tomli_w

from phd_artifacts.config import load_config
from phd_artifacts.runs import Run


def compute_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Compute the SHA-256 checksum of a file."""

    digest = hashlib.sha256()

    with path.open("rb") as file:
        while chunk := file.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()


def get_checkpoint_store(project_name: str) -> Path:
    config = load_config()

    artifact_root = Path(config["artifact_root"])

    return artifact_root / project_name / "checkpoints"


def get_artifact_version(run: Run) -> str:
    timestamp = run.created_at or run.modified_at

    return f"{timestamp:%Y%m%d_%H%M%S}_{run.id}"


def promote_checkpoint(
    project_name: str,
    run: Run,
    checkpoint: Path,
    name: str,
) -> Path:
    """Promote a run checkpoint into the persistent artifact store."""

    store = get_checkpoint_store(project_name)
    version = get_artifact_version(run)

    destination = store / name / version

    if destination.exists():
        raise FileExistsError(f"Artifact already exists: {destination}")

    destination.mkdir(parents=True)

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

        if source.exists():
            shutil.copy2(
                source,
                destination / filename,
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
            "size_bytes": checkpoint_destination.stat().st_size,
            "sha256": compute_sha256(checkpoint_destination),
        },
    }

    if run.created_at:
        metadata["run_created_at"] = run.created_at.isoformat()

    with (destination / "metadata.toml").open("wb") as file:
        tomli_w.dump(metadata, file)

    return destination
