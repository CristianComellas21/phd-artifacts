import hashlib
from dataclasses import dataclass
from pathlib import Path

from phd_artifacts.artifacts.models import Artifact


@dataclass
class FileVerification:
    path: str
    exists: bool
    size_ok: bool
    sha256_ok: bool


@dataclass
class VerificationResult:
    files: list[FileVerification]

    @property
    def ok(self) -> bool:
        return all(item.exists and item.size_ok and item.sha256_ok for item in self.files)


def compute_sha256(
    path: Path,
    chunk_size: int = 1024 * 1024,
) -> str:
    """Compute the SHA-256 checksum of a file."""

    digest = hashlib.sha256()

    with path.open("rb") as file:
        while chunk := file.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()


def _verify_file(
    artifact_path: Path,
    file_info: dict,
) -> FileVerification:
    relative_path = file_info["path"]
    path = artifact_path / relative_path

    if not path.is_file():
        return FileVerification(
            path=relative_path,
            exists=False,
            size_ok=False,
            sha256_ok=False,
        )

    size_ok = path.stat().st_size == file_info["size_bytes"]

    sha256_ok = compute_sha256(path) == file_info["sha256"]

    return FileVerification(
        path=relative_path,
        exists=True,
        size_ok=size_ok,
        sha256_ok=sha256_ok,
    )


def verify_artifact(
    artifact: Artifact,
) -> VerificationResult:
    """Verify all checkpoint and portable files in an artifact."""

    metadata = artifact.metadata

    checkpoints = metadata.get(
        "checkpoints",
        {},
    )

    if not checkpoints:
        raise ValueError("Artifact does not define any checkpoints.")

    files: list[FileVerification] = []

    for checkpoint in checkpoints.values():
        files.append(
            _verify_file(
                artifact.path,
                checkpoint,
            )
        )

        for portable in checkpoint.get(
            "portable_files",
            [],
        ):
            files.append(
                _verify_file(
                    artifact.path,
                    portable,
                )
            )

    return VerificationResult(
        files=files,
    )
