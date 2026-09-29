from pathlib import PurePosixPath

from phd_artifacts.artifacts.models import Artifact
from phd_artifacts.artifacts.verification import verify_artifact
from phd_artifacts.remotes import get_remote
from phd_artifacts.remotes.backends.registry import get_backend


def push_artifact(
    artifact: Artifact,
    remote_name: str,
) -> str:
    """Push a promoted artifact to a configured remote."""

    valid, _, _ = verify_artifact(artifact)

    if not valid:
        raise RuntimeError(f"Artifact '{artifact.name}' failed integrity verification.")

    remote = get_remote(remote_name)
    backend = get_backend(remote.type)

    remote_path = PurePosixPath(*artifact.relative_path.parts)

    return backend.push(remote=remote, source=artifact.path, remote_path=remote_path)
