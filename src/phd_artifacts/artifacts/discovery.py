import tomllib
from pathlib import Path

from phd_artifacts.artifacts.models import Artifact
from phd_artifacts.core.config import load_config


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
                relative_path=artifact_path.relative_to(artifact_root),
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
