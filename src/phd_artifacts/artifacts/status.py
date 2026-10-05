from dataclasses import dataclass
from pathlib import PurePosixPath

from phd_artifacts.artifacts.models import Artifact
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


def get_artifact_remote_states(
    artifacts: list[Artifact],
    remote_name: str,
    progress: ProgressReporter = NULL_PROGRESS,
) -> list[ArtifactRemoteState]:
    """Compare multiple local artifacts against a remote."""

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
