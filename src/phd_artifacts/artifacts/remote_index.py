import json
from dataclasses import dataclass
from pathlib import PurePosixPath

from phd_artifacts.artifacts.exceptions import RemoteIndexError
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


def _deserialize_index(
    text: str,
    remote_name: str,
) -> RemoteIndex:
    try:
        data = json.loads(text)

    except json.JSONDecodeError as exc:
        raise RemoteIndexError(
            remote_name=remote_name,
            operation="read",
            message="Remote index contains invalid JSON.",
        ) from exc

    version = data.get("version")

    if version != INDEX_VERSION:
        raise RemoteIndexError(
            remote_name=remote_name,
            operation="read",
            message=f"Unsupported remote index version: {version}",
        )

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

    try:
        text = backend.read_text(
            remote=remote,
            remote_path=INDEX_PATH,
        )

        return _deserialize_index(text, remote_name)

    except RemoteIndexError:
        raise

    except Exception as exc:
        raise RemoteIndexError(
            remote_name=remote_name,
            operation="read",
            message="Could not read remote index.",
        ) from exc


def write_remote_index(
    remote_name: str,
    index: RemoteIndex,
) -> None:
    remote = get_remote(remote_name)
    backend = get_backend(remote.type)

    try:
        backend.write_text(
            remote=remote,
            remote_path=INDEX_PATH,
            text=_serialize_index(index),
        )

    except Exception as exc:
        raise RemoteIndexError(
            remote_name=remote_name,
            operation="write",
            message="Could not write remote index.",
        ) from exc


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
    remove_remote_index_entries(
        remote_name=remote_name,
        artifact_paths=[artifact_path],
    )


def remove_remote_index_entries(
    remote_name: str,
    artifact_paths: list[PurePosixPath],
) -> None:
    index = read_remote_index(remote_name)

    paths = set(artifact_paths)

    updated = RemoteIndex(
        version=index.version,
        artifacts=[entry for entry in index.artifacts if entry.path not in paths],
    )

    write_remote_index(
        remote_name=remote_name,
        index=updated,
    )
