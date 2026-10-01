import tomllib
from pathlib import PurePosixPath

from phd_artifacts.artifacts.models import RemoteArtifact
from phd_artifacts.remotes import get_remote
from phd_artifacts.remotes.backends.registry import get_backend


def discover_remote_artifacts(
    remote_name: str,
) -> list[RemoteArtifact]:
    remote = get_remote(remote_name)
    backend = get_backend(remote.type)

    entries = backend.list_recursive(
        remote=remote,
        remote_path=PurePosixPath(),
    )

    metadata_entries = [
        entry for entry in entries if not entry.is_dir and entry.name == "metadata.toml"
    ]

    artifacts: list[RemoteArtifact] = []

    for entry in metadata_entries:
        content = backend.read_text(
            remote=remote,
            remote_path=entry.path,
        )

        metadata = tomllib.loads(content)

        artifact_path = entry.path.parent

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
