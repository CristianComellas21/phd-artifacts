import hashlib
from pathlib import Path

from phd_artifacts.artifacts.models import Artifact


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
