from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from phd_artifacts.artifacts.models import Artifact, RemoteArtifact
from phd_artifacts.core.config import load_config
from phd_artifacts.core.progress import NULL_PROGRESS, ProgressReporter
from phd_artifacts.remotes import get_remote
from phd_artifacts.remotes.backends.registry import get_backend
from phd_artifacts.remotes.status import RemoteComparison, RemoteStatus


@dataclass
class ArtifactRemoteState:
    artifact: Artifact
    comparison: RemoteComparison

    @property
    def status(self) -> RemoteStatus:
        return self.comparison.status

    @property
    def pending(self) -> bool:
        return self.status is not RemoteStatus.UP_TO_DATE


@dataclass
class RemoteArtifactLocalState:
    artifact: RemoteArtifact
    status: RemoteStatus

    @property
    def pending(self) -> bool:
        return self.status is not RemoteStatus.UP_TO_DATE


def get_artifact_remote_states(
    artifacts: list[Artifact],
    remote_name: str,
    progress: ProgressReporter = NULL_PROGRESS,
) -> list[ArtifactRemoteState]:
    """Compare local artifacts against a remote."""

    remote = get_remote(remote_name)
    backend = get_backend(remote.type)

    states: list[ArtifactRemoteState] = []
    total = len(artifacts)

    for index, artifact in enumerate(artifacts, start=1):
        progress.update(f"Checking '{artifact.name}' ({index}/{total})")

        remote_path = PurePosixPath(*artifact.relative_path.parts)

        comparison = backend.compare(
            remote=remote,
            source=artifact.path,
            remote_path=remote_path,
        )

        states.append(
            ArtifactRemoteState(
                artifact=artifact,
                comparison=comparison,
            )
        )

    return states


def get_remote_artifact_local_states(
    artifacts: list[RemoteArtifact],
    progress: ProgressReporter = NULL_PROGRESS,
) -> list[RemoteArtifactLocalState]:
    """Compare remote artifacts against the local artifact store."""

    config = load_config()
    artifact_root = Path(config["artifact_root"])

    states: list[RemoteArtifactLocalState] = []
    total = len(artifacts)

    for index, artifact in enumerate(artifacts, start=1):
        progress.update(f"Checking '{artifact.name}' ({index}/{total})")

        destination = artifact_root / Path(*artifact.path.parts)

        if not destination.exists():
            states.append(
                RemoteArtifactLocalState(
                    artifact=artifact,
                    status=RemoteStatus.MISSING,
                )
            )
            continue

        remote = get_remote(artifact.remote)
        backend = get_backend(remote.type)

        comparison = backend.compare(
            remote=remote,
            source=destination,
            remote_path=artifact.path,
        )

        states.append(
            RemoteArtifactLocalState(
                artifact=artifact,
                status=comparison.status,
            )
        )

    return states
