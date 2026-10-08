import tomllib
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from phd_artifacts.artifacts.fingerprint import compute_artifact_fingerprint
from phd_artifacts.artifacts.models import Artifact, RemoteArtifact
from phd_artifacts.artifacts.remote_index import read_remote_index
from phd_artifacts.core.config import load_config
from phd_artifacts.core.progress import NULL_PROGRESS, ProgressReporter
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
    """Compare local artifacts against the remote index."""

    progress.update("Reading remote index")

    remote_index = read_remote_index(remote_name)

    remote_entries = {entry.path: entry for entry in remote_index.artifacts}

    states: list[ArtifactRemoteState] = []
    total = len(artifacts)

    for index, artifact in enumerate(artifacts, start=1):
        progress.update(f"Checking '{artifact.name}' ({index}/{total})")

        remote_path = PurePosixPath(*artifact.relative_path.parts)
        remote_entry = remote_entries.get(remote_path)

        if remote_entry is None:
            status = RemoteStatus.MISSING
        else:
            local_fingerprint = compute_artifact_fingerprint(artifact)

            if local_fingerprint == remote_entry.fingerprint:
                status = RemoteStatus.UP_TO_DATE
            else:
                status = RemoteStatus.DIFFERENT

        states.append(
            ArtifactRemoteState(
                artifact=artifact,
                comparison=RemoteComparison(
                    status=status,
                ),
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

        if not destination.is_dir():
            states.append(
                RemoteArtifactLocalState(
                    artifact=artifact,
                    status=RemoteStatus.MISSING,
                )
            )
            continue

        metadata_path = destination / "metadata.toml"

        if not metadata_path.is_file():
            states.append(
                RemoteArtifactLocalState(
                    artifact=artifact,
                    status=RemoteStatus.DIFFERENT,
                )
            )
            continue

        try:
            with metadata_path.open("rb") as file:
                metadata = tomllib.load(file)

        except (OSError, tomllib.TOMLDecodeError):
            states.append(
                RemoteArtifactLocalState(
                    artifact=artifact,
                    status=RemoteStatus.DIFFERENT,
                )
            )
            continue

        local_artifact = Artifact(
            path=destination,
            relative_path=Path(*artifact.path.parts),
            project=artifact.project,
            artifact_type=artifact.artifact_type,
            name=artifact.name,
            version=artifact.version,
            metadata=metadata,
        )

        local_fingerprint = compute_artifact_fingerprint(local_artifact)
        remote_fingerprint = compute_artifact_fingerprint(artifact)

        if local_fingerprint == remote_fingerprint:
            status = RemoteStatus.UP_TO_DATE
        else:
            status = RemoteStatus.DIFFERENT

        states.append(
            RemoteArtifactLocalState(
                artifact=artifact,
                status=status,
            )
        )

    return states
