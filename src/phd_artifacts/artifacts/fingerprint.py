import hashlib
import json

from phd_artifacts.artifacts.models import Artifact, RemoteArtifact


def compute_artifact_fingerprint(
    artifact: Artifact | RemoteArtifact,
) -> str:
    """Compute a stable fingerprint from artifact metadata."""

    checkpoints = artifact.metadata.get("checkpoints", {})

    files: list[dict] = []

    for role, checkpoint in sorted(checkpoints.items()):
        files.append(
            {
                "role": role,
                "path": checkpoint["path"],
                "size_bytes": checkpoint["size_bytes"],
                "sha256": checkpoint["sha256"],
            }
        )

        for portable in sorted(
            checkpoint.get("portable_files", []),
            key=lambda item: item["path"],
        ):
            files.append(
                {
                    "role": role,
                    "path": portable["path"],
                    "size_bytes": portable["size_bytes"],
                    "sha256": portable["sha256"],
                }
            )

    payload = {
        "project": artifact.project,
        "type": artifact.artifact_type,
        "name": artifact.name,
        "version": artifact.version,
        "files": files,
    }

    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()
