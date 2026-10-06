import shutil
from dataclasses import dataclass
from pathlib import Path

from phd_artifacts.artifacts.models import Artifact, RemoteArtifact
from phd_artifacts.artifacts.remote_index import remove_remote_index_entry
from phd_artifacts.core.config import load_config
from phd_artifacts.remotes import get_remote
from phd_artifacts.remotes.backends.registry import get_backend


def remove_artifact(artifact: Artifact) -> None:
    config = load_config()
    artifact_root = Path(config["artifact_root"]).resolve()
    artifact_path = artifact.path.resolve()

    if artifact_root not in artifact_path.parents:
        raise RuntimeError(f"Refusing to remove artifact outside artifact store: {artifact_path}")

    shutil.rmtree(artifact_path)


@dataclass
class PreparedRemoteRemoval:
    artifact: RemoteArtifact


def prepare_remote_removal(
    artifact: RemoteArtifact,
) -> PreparedRemoteRemoval:
    return PreparedRemoteRemoval(
        artifact=artifact,
    )


def perform_remote_removal(
    prepared: PreparedRemoteRemoval,
) -> None:
    remote = get_remote(prepared.artifact.remote)
    backend = get_backend(remote.type)

    backend.remove(
        remote=remote,
        remote_path=prepared.artifact.path,
    )


def finalize_remote_removal(
    prepared: PreparedRemoteRemoval,
) -> None:
    remove_remote_index_entry(
        remote_name=prepared.artifact.remote,
        artifact_path=prepared.artifact.path,
    )
