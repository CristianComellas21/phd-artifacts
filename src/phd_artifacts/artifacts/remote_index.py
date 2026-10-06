import json
from dataclasses import dataclass
from pathlib import PurePosixPath

from phd_artifacts.artifacts.models import Artifact, RemoteArtifact
from phd_artifacts.remotes.backends.registry import get_backend
from phd_artifacts.remotes.service import get_remote

INDEX_PATH = PurePosixPath("index.json")
INDEX_VERSION = 1


@dataclass
class RemoteIndexEntry:
    path: PurePosixPath
    metadata: dict


@dataclass
class RemoteIndex:
    version: int
    artifacts: list[RemoteIndexEntry]


def _serialize_index(index: RemoteIndex) -> str:
    data = {
        "version": index.version,
        "artifacts": [
            {
                "path": entry.path.as_posix(),
                "metadata": entry.metadata,
            }
            for entry in index.artifacts
        ],
    }

    return json.dumps(
        data,
        indent=2,
        ensure_ascii=False,
    )


def _deserialize_index(text: str) -> RemoteIndex:
    data = json.loads(text)

    return RemoteIndex(
        version=data["version"],
        artifacts=[
            RemoteIndexEntry(
                path=PurePosixPath(entry["path"]),
                metadata=entry["metadata"],
            )
            for entry in data["artifacts"]
        ],
    )


def _entry_from_artifact(
    artifact: Artifact,
) -> RemoteIndexEntry:
    return RemoteIndexEntry(
        path=PurePosixPath(*artifact.relative_path.parts),
        metadata=artifact.metadata,
    )


def read_remote_index(
    remote_name: str,
) -> RemoteIndex:
    remote = get_remote(remote_name)
    backend = get_backend(remote.type)

    text = backend.read_text(
        remote=remote,
        remote_path=INDEX_PATH,
    )

    return _deserialize_index(text)


def write_remote_index(
    remote_name: str,
    index: RemoteIndex,
) -> None:
    remote = get_remote(remote_name)
    backend = get_backend(remote.type)

    backend.write_text(
        remote=remote,
        remote_path=INDEX_PATH,
        text=_serialize_index(index),
    )


def rebuild_remote_index(
    remote_name: str,
) -> RemoteIndex:
    from phd_artifacts.artifacts.discovery import scan_remote_artifacts

    artifacts = scan_remote_artifacts(remote_name)

    index = RemoteIndex(
        version=INDEX_VERSION,
        artifacts=[
            RemoteIndexEntry(
                path=artifact.path,
                metadata=artifact.metadata,
            )
            for artifact in artifacts
        ],
    )

    write_remote_index(
        remote_name=remote_name,
        index=index,
    )

    return index


def remote_artifacts_from_index(
    remote_name: str,
    index: RemoteIndex,
) -> list[RemoteArtifact]:
    return [
        RemoteArtifact(
            remote=remote_name,
            path=entry.path,
            project=entry.metadata.get("project", ""),
            artifact_type=entry.metadata.get("type", ""),
            name=entry.metadata.get("name", ""),
            version=entry.path.name,
            metadata=entry.metadata,
        )
        for entry in index.artifacts
    ]


def add_artifact_to_remote_index(
    remote_name: str,
    artifact: Artifact,
) -> None: ...


def remove_artifact_from_remote_index(
    remote_name: str,
    path: PurePosixPath,
) -> None: ...


def upsert_remote_index_entry(
    remote_name: str,
    artifact: Artifact,
) -> None:
    index = read_remote_index(remote_name)

    entry = _entry_from_artifact(artifact)

    artifacts = [current for current in index.artifacts if current.path != entry.path]

    artifacts.append(entry)

    updated = RemoteIndex(
        version=index.version,
        artifacts=artifacts,
    )

    write_remote_index(
        remote_name=remote_name,
        index=updated,
    )


def remove_remote_index_entry(
    remote_name: str,
    artifact_path: PurePosixPath,
) -> None:
    index = read_remote_index(remote_name)

    updated = RemoteIndex(
        version=index.version,
        artifacts=[entry for entry in index.artifacts if entry.path != artifact_path],
    )

    write_remote_index(
        remote_name=remote_name,
        index=updated,
    )
