import yaml

from phd_artifacts.artifacts.models import Artifact, RemoteArtifact
from phd_artifacts.core.config_filtering import (
    ConfigFilter,
    matches_config,
    matches_config_any,
)
from phd_artifacts.remotes.backends.registry import get_backend
from phd_artifacts.remotes.service import get_remote


def load_artifact_config(
    artifact: Artifact,
) -> dict | None:
    """Load the stored config for a local artifact."""

    path = artifact.path / "config.yaml"

    if not path.is_file():
        return None

    try:
        with path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
    except (OSError, yaml.YAMLError):
        return None

    if not isinstance(config, dict):
        return None

    return config


def load_remote_artifact_config(
    artifact: RemoteArtifact,
) -> dict | None:
    """Load the stored config for a remote artifact."""

    remote = get_remote(artifact.remote)
    backend = get_backend(remote.type)

    try:
        content = backend.read_text(
            remote=remote,
            remote_path=artifact.path / "config.yaml",
        )

        config = yaml.safe_load(content)

    except (RuntimeError, yaml.YAMLError):
        return None

    if not isinstance(config, dict):
        return None

    return config


def filter_artifacts_by_config(
    artifacts: list[Artifact],
    filters: list[ConfigFilter],
    any_filters: list[ConfigFilter] | None = None,
) -> list[Artifact]:
    """Filter local artifacts using their stored configurations."""

    if not filters and not any_filters:
        return artifacts

    matches: list[Artifact] = []

    for artifact in artifacts:
        config = load_artifact_config(artifact)

        if config is None:
            continue

        if filters and not matches_config(
            config,
            filters,
        ):
            continue

        if any_filters and not matches_config_any(
            config,
            any_filters,
        ):
            continue

        matches.append(artifact)

    return matches


def filter_remote_artifacts_by_config(
    artifacts: list[RemoteArtifact],
    filters: list[ConfigFilter],
    any_filters: list[ConfigFilter] | None = None,
) -> list[RemoteArtifact]:
    """Filter remote artifacts using their stored configurations."""

    if not filters and not any_filters:
        return artifacts

    matches: list[RemoteArtifact] = []

    for artifact in artifacts:
        config = load_remote_artifact_config(artifact)

        if config is None:
            continue

        if filters and not matches_config(
            config,
            filters,
        ):
            continue

        if any_filters and not matches_config_any(
            config,
            any_filters,
        ):
            continue

        matches.append(artifact)

    return matches
