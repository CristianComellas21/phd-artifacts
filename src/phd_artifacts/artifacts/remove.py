import shutil
from pathlib import Path

from phd_artifacts.artifacts.models import Artifact
from phd_artifacts.core.config import load_config


def remove_artifact(artifact: Artifact) -> None:
    config = load_config()
    artifact_root = Path(config["artifact_root"]).resolve()
    artifact_path = artifact.path.resolve()

    if artifact_root not in artifact_path.parents:
        raise RuntimeError(f"Refusing to remove artifact outside artifact store: {artifact_path}")

    shutil.rmtree(artifact_path)
