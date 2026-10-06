import tomllib
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path, PurePosixPath

from phd_artifacts.artifacts.models import Artifact, RemoteArtifact
from phd_artifacts.core.config import load_config
from phd_artifacts.remotes.backends.registry import get_backend
from phd_artifacts.remotes.service import get_remote


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


def _read_remote_metadata(
    backend,
    remote,
    path: PurePosixPath,
) -> tuple[PurePosixPath, dict]:
    text = backend.read_text(
        remote=remote,
        remote_path=path,
    )

    return path, tomllib.loads(text)


def scan_remote_artifacts(
    remote_name: str,
) -> list[RemoteArtifact]:
    remote = get_remote(remote_name)
    backend = get_backend(remote.type)

    entries = backend.list_recursive(
        remote=remote,
        remote_path=PurePosixPath(),
    )

    metadata_paths = [
        entry.path for entry in entries if not entry.is_dir and entry.name == "metadata.toml"
    ]

    artifacts: list[RemoteArtifact] = []

    reader = partial(
        _read_remote_metadata,
        backend,
        remote,
    )

    with ThreadPoolExecutor(max_workers=4) as executor:
        metadata_results = list(
            executor.map(
                reader,
                metadata_paths,
            )
        )

    for metadata_path, metadata in metadata_results:
        artifact_path = metadata_path.parent

        artifacts.append(
            RemoteArtifact(
                remote=remote_name,
                path=artifact_path,
                project=metadata.get("project", ""),
                artifact_type=metadata.get("type", ""),
                name=metadata.get("name", ""),
                version=artifact_path.name,
                metadata=metadata,
            )
        )

    return artifacts
