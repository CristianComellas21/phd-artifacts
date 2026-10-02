from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath

from phd_artifacts.artifacts.exceptions import RemoteArtifactConflictError
from phd_artifacts.artifacts.models import Artifact
from phd_artifacts.artifacts.verification import verify_artifact
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
