import shutil
import tomllib
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path, PurePosixPath

from phd_artifacts.artifacts.exceptions import (
    LocalArtifactConflictError,
    RemoteArtifactConflictError,
)
from phd_artifacts.artifacts.models import Artifact, RemoteArtifact
from phd_artifacts.artifacts.verification import verify_artifact
from phd_artifacts.core.config import load_config
from phd_artifacts.remotes import get_remote
from phd_artifacts.remotes.backends.registry import get_backend
from phd_artifacts.remotes.status import RemoteComparison, RemoteStatus


class PushAction(StrEnum):
    UPLOADED = "uploaded"
    ALREADY_UP_TO_DATE = "already_up_to_date"
    OVERWRITTEN = "overwritten"


@dataclass
class PushResult:
    destination: str
    action: PushAction


class PullAction(StrEnum):
    DOWNLOADED = "downloaded"
    ALREADY_UP_TO_DATE = "already_up_to_date"
    OVERWRITTEN = "overwritten"


@dataclass
class PullResult:
    destination: Path
    action: PullAction


def push_artifact(
    artifact: Artifact,
    remote_name: str,
    force: bool = False,
) -> PushResult:
    """Push a promoted artifact to a configured remote."""

    verification = verify_artifact(artifact)

    if not verification.ok:
        raise RuntimeError(f"Artifact '{artifact.name}' failed integrity verification.")

    remote = get_remote(remote_name)
    backend = get_backend(remote.type)

    remote_path = PurePosixPath(*artifact.relative_path.parts)

    comparison = backend.compare(
        remote=remote,
        source=artifact.path,
        remote_path=remote_path,
    )

    destination = backend.get_target(
        remote=remote,
        remote_path=remote_path,
    )

    if comparison.status is RemoteStatus.UP_TO_DATE:
        return PushResult(
            destination=destination,
            action=PushAction.ALREADY_UP_TO_DATE,
        )

    if comparison.status is RemoteStatus.DIFFERENT:
        if not force:
            raise RemoteArtifactConflictError(
                name=artifact.name,
                remote_name=remote_name,
            )

        backend.push(
            remote=remote,
            source=artifact.path,
            remote_path=remote_path,
        )

        return PushResult(
            destination=destination,
            action=PushAction.OVERWRITTEN,
        )

    backend.push(
        remote=remote,
        source=artifact.path,
        remote_path=remote_path,
    )

    return PushResult(
        destination=destination,
        action=PushAction.UPLOADED,
    )


def pull_artifact(
    artifact: RemoteArtifact,
    force: bool = False,
) -> PullResult:
    """Pull a remote artifact into the local artifact store."""

    config = load_config()

    artifact_root = Path(config["artifact_root"])

    destination = artifact_root / Path(*artifact.path.parts)

    remote = get_remote(artifact.remote)
    backend = get_backend(remote.type)

    if destination.exists():
        comparison = backend.compare(
            remote=remote,
            source=destination,
            remote_path=artifact.path,
        )

        if comparison.status is RemoteStatus.UP_TO_DATE:
            return PullResult(
                destination=destination,
                action=PullAction.ALREADY_UP_TO_DATE,
            )

        if not force:
            raise LocalArtifactConflictError(
                name=artifact.name,
                remote_name=artifact.remote,
            )

        shutil.rmtree(
            destination,
        )

        action = PullAction.OVERWRITTEN

    else:
        action = PullAction.DOWNLOADED

    backend.pull(
        remote=remote,
        remote_path=artifact.path,
        destination=destination,
    )

    metadata_path = destination / "metadata.toml"

    try:
        with metadata_path.open("rb") as file:
            metadata = tomllib.load(file)

        local_artifact = Artifact(
            path=destination,
            relative_path=Path(*artifact.path.parts),
            project=artifact.project,
            artifact_type=artifact.artifact_type,
            name=artifact.name,
            version=artifact.version,
            metadata=metadata,
        )

        verification = verify_artifact(local_artifact)

        if not verification.ok:
            raise RuntimeError(
                f"Downloaded artifact '{artifact.name}' failed integrity verification."
            )

    except Exception:
        shutil.rmtree(
            destination,
            ignore_errors=True,
        )
        raise

    return PullResult(
        destination=destination,
        action=action,
    )


def get_artifact_remote_status(
    artifact: Artifact,
    remote_name: str,
) -> RemoteComparison:
    """Compare a local artifact with its remote copy."""

    remote = get_remote(remote_name)
    backend = get_backend(remote.type)

    remote_path = PurePosixPath(*artifact.relative_path.parts)

    return backend.compare(
        remote=remote,
        source=artifact.path,
        remote_path=remote_path,
    )
