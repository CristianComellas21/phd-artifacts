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
from phd_artifacts.core.progress import NULL_PROGRESS, ProgressReporter
from phd_artifacts.remotes import get_remote
from phd_artifacts.remotes.backends.registry import get_backend
from phd_artifacts.remotes.status import RemoteComparison, RemoteStatus


class PushAction(StrEnum):
    UPLOADED = "uploaded"
    ALREADY_UP_TO_DATE = "already_up_to_date"
    OVERWRITTEN = "overwritten"


@dataclass
class PreparedPush:
    artifact: Artifact
    remote_name: str
    remote_path: PurePosixPath
    destination: str
    action: PushAction


@dataclass
class PushResult:
    destination: str
    action: PushAction


class PullAction(StrEnum):
    DOWNLOADED = "downloaded"
    ALREADY_UP_TO_DATE = "already_up_to_date"
    OVERWRITTEN = "overwritten"


@dataclass
class PreparedPull:
    artifact: RemoteArtifact
    destination: Path
    action: PullAction


@dataclass
class PullResult:
    destination: Path
    action: PullAction


def prepare_push(
    artifact: Artifact,
    remote_name: str,
    force: bool = False,
    progress: ProgressReporter = NULL_PROGRESS,
) -> PreparedPush:
    """Validate and prepare an artifact push without transferring data."""

    progress.update("Verifying local artifact")

    verification = verify_artifact(artifact)

    if not verification.ok:
        raise RuntimeError(f"Artifact '{artifact.name}' failed integrity verification.")

    progress.update(f"Connecting to remote '{remote_name}'")

    remote = get_remote(remote_name)
    backend = get_backend(remote.type)

    remote_path = PurePosixPath(*artifact.relative_path.parts)

    progress.update("Comparing local and remote artifact")

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
        action = PushAction.ALREADY_UP_TO_DATE

    elif comparison.status is RemoteStatus.DIFFERENT:
        if not force:
            raise RemoteArtifactConflictError(
                name=artifact.name,
                remote_name=remote_name,
            )

        action = PushAction.OVERWRITTEN

    else:
        action = PushAction.UPLOADED

    return PreparedPush(
        artifact=artifact,
        remote_name=remote_name,
        remote_path=remote_path,
        destination=destination,
        action=action,
    )


def perform_push(
    prepared: PreparedPush,
) -> PushResult:
    """Perform a previously prepared artifact push."""

    if prepared.action is PushAction.ALREADY_UP_TO_DATE:
        return PushResult(
            destination=prepared.destination,
            action=prepared.action,
        )

    remote = get_remote(prepared.remote_name)
    backend = get_backend(remote.type)

    backend.push(
        remote=remote,
        source=prepared.artifact.path,
        remote_path=prepared.remote_path,
    )

    return PushResult(
        destination=prepared.destination,
        action=prepared.action,
    )


def prepare_pull(
    artifact: RemoteArtifact,
    force: bool = False,
    progress: ProgressReporter = NULL_PROGRESS,
) -> PreparedPull:
    """Validate and prepare an artifact pull without transferring data."""

    config = load_config()
    artifact_root = Path(config["artifact_root"])

    destination = artifact_root / Path(*artifact.path.parts)

    if not destination.exists():
        return PreparedPull(
            artifact=artifact,
            destination=destination,
            action=PullAction.DOWNLOADED,
        )

    progress.update("Comparing local and remote artifact")

    remote = get_remote(artifact.remote)
    backend = get_backend(remote.type)

    comparison = backend.compare(
        remote=remote,
        source=destination,
        remote_path=artifact.path,
    )

    if comparison.status is RemoteStatus.UP_TO_DATE:
        return PreparedPull(
            artifact=artifact,
            destination=destination,
            action=PullAction.ALREADY_UP_TO_DATE,
        )

    if not force:
        raise LocalArtifactConflictError(
            name=artifact.name,
            remote_name=artifact.remote,
        )

    return PreparedPull(
        artifact=artifact,
        destination=destination,
        action=PullAction.OVERWRITTEN,
    )


def perform_pull(
    prepared: PreparedPull,
) -> PullResult:
    """Perform a previously prepared artifact pull."""

    if prepared.action is PullAction.ALREADY_UP_TO_DATE:
        return PullResult(
            destination=prepared.destination,
            action=prepared.action,
        )

    if prepared.action is PullAction.OVERWRITTEN:
        shutil.rmtree(prepared.destination)

    remote = get_remote(prepared.artifact.remote)
    backend = get_backend(remote.type)

    try:
        backend.pull(
            remote=remote,
            remote_path=prepared.artifact.path,
            destination=prepared.destination,
        )

    except Exception:
        shutil.rmtree(
            prepared.destination,
            ignore_errors=True,
        )
        raise

    return PullResult(
        destination=prepared.destination,
        action=prepared.action,
    )


def verify_pulled_artifact(
    prepared: PreparedPull,
    progress: ProgressReporter = NULL_PROGRESS,
) -> None:
    """Validate a downloaded artifact and remove it if verification fails."""

    if prepared.action is PullAction.ALREADY_UP_TO_DATE:
        return

    progress.update("Reading downloaded metadata")

    metadata_path = prepared.destination / "metadata.toml"

    try:
        with metadata_path.open("rb") as file:
            metadata = tomllib.load(file)

        local_artifact = Artifact(
            path=prepared.destination,
            relative_path=Path(*prepared.artifact.path.parts),
            project=prepared.artifact.project,
            artifact_type=prepared.artifact.artifact_type,
            name=prepared.artifact.name,
            version=prepared.artifact.version,
            metadata=metadata,
        )

        progress.update("Verifying downloaded artifact")

        verification = verify_artifact(local_artifact)

        if not verification.ok:
            raise RuntimeError(
                f"Downloaded artifact '{prepared.artifact.name}' failed integrity verification."
            )

    except Exception:
        shutil.rmtree(
            prepared.destination,
            ignore_errors=True,
        )
        raise


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
