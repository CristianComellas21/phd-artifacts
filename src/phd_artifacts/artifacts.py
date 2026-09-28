import hashlib
import platform
import shutil
import tomllib
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import tomli_w

from phd_artifacts.config import load_config
from phd_artifacts.filtering import is_since, matches_text
from phd_artifacts.runs import Run


@dataclass
class Artifact:
    path: Path
    project: str
    artifact_type: str
    name: str
    version: str
    metadata: dict


def filter_artifacts(
    artifacts: list[Artifact],
    project: str | None = None,
    artifact_type: str | None = None,
    name: str | None = None,
    experiment: str | None = None,
    model: str | None = None,
    since: timedelta | None = None,
) -> list[Artifact]:
    """Filter promoted artifacts by their metadata."""

    filtered: list[Artifact] = []

    for artifact in artifacts:
        metadata = artifact.metadata

        promoted_at: datetime | None = None
        promoted_at_raw = metadata.get("promoted_at")

        if promoted_at_raw:
            try:
                promoted_at = datetime.fromisoformat(promoted_at_raw)
            except ValueError:
                pass

        if not matches_text(artifact.project, project):
            continue

        if not matches_text(artifact.artifact_type, artifact_type):
            continue

        if not matches_text(artifact.name, name):
            continue

        if not matches_text(
            metadata.get("experiment"),
            experiment,
        ):
            continue

        if not matches_text(
            metadata.get("model"),
            model,
        ):
            continue

        if not is_since(promoted_at, since):
            continue

        filtered.append(artifact)

    return filtered


def discover_artifacts() -> list[Artifact]:
    """Discover promoted artifacts in the artifact store."""

    config = load_config()
    artifact_root = Path(config["artifact_root"])

    if not artifact_root.exists():
        return []

    artifacts: list[Artifact] = []

    metadata_files = artifact_root.rglob("metadata.toml")

    for metadata_path in metadata_files:
        try:
            with metadata_path.open("rb") as file:
                metadata = tomllib.load(file)
        except (OSError, tomllib.TOMLDecodeError):
            continue

        project = metadata.get("project")

        artifact_path = metadata_path.parent

        artifacts.append(
            Artifact(
                path=artifact_path,
                project=project or "",
                artifact_type=metadata.get("type", ""),
                name=metadata.get("name", ""),
                version=artifact_path.name,
                metadata=metadata,
            )
        )

    artifacts.sort(
        key=lambda artifact: artifact.metadata.get(
            "promoted_at",
            "",
        ),
        reverse=True,
    )

    return artifacts


def compute_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Compute the SHA-256 checksum of a file."""

    digest = hashlib.sha256()

    with path.open("rb") as file:
        while chunk := file.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()


def verify_artifact(artifact: Artifact) -> tuple[bool, str, str]:
    """Verify the checksum of a checkpoint artifact."""

    artifact_info = artifact.metadata.get("artifact", {})

    checkpoint_name = artifact_info.get("checkpoint")
    expected_sha256 = artifact_info.get("sha256")

    if not checkpoint_name:
        raise ValueError("Artifact does not define a checkpoint file.")

    if not expected_sha256:
        raise ValueError("Artifact does not contain a stored SHA-256 checksum.")

    checkpoint_path = artifact.path / checkpoint_name

    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_path}")

    actual_sha256 = compute_sha256(checkpoint_path)

    return (
        actual_sha256 == expected_sha256,
        expected_sha256,
        actual_sha256,
    )


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
