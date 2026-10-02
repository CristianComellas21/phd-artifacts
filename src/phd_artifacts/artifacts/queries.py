from datetime import datetime, timedelta

from phd_artifacts.artifacts.config import (
    filter_artifacts_by_config,
    filter_remote_artifacts_by_config,
)
from phd_artifacts.artifacts.discovery import (
    discover_artifacts,
    discover_remote_artifacts,
)
from phd_artifacts.artifacts.exceptions import (
    ArtifactAmbiguousError,
    ArtifactNotFoundError,
    RemoteArtifactAmbiguousError,
    RemoteArtifactNotFoundError,
)
from phd_artifacts.artifacts.filtering import filter_artifacts
from phd_artifacts.artifacts.models import Artifact, RemoteArtifact
from phd_artifacts.core.config_filtering import ConfigFilter
from phd_artifacts.core.filtering import is_since, matches_text


def get_artifacts(
    project: str | None = None,
    artifact_type: str | None = None,
    name: str | None = None,
    experiment: str | None = None,
    model: str | None = None,
    since: timedelta | None = None,
    config_filters: list[ConfigFilter] | None = None,
    config_any_filters: list[ConfigFilter] | None = None,
) -> list[Artifact]:
    """Get promoted artifacts matching the requested filters."""

    artifacts = discover_artifacts()

    artifacts = filter_artifacts(
        artifacts,
        project=project,
        artifact_type=artifact_type,
        name=name,
        experiment=experiment,
        model=model,
        since=since,
    )

    if config_filters or config_any_filters:
        artifacts = filter_artifacts_by_config(
            artifacts,
            filters=config_filters or [],
            any_filters=config_any_filters or [],
        )

    return artifacts


def get_artifact(
    name: str,
    version: str | None = None,
    project: str | None = None,
) -> Artifact:
    """Resolve exactly one promoted artifact."""

    artifacts = discover_artifacts()

    artifacts = [
        artifact
        for artifact in artifacts
        if artifact.name == name and (project is None or artifact.project == project)
    ]

    if version is not None:
        artifacts = [artifact for artifact in artifacts if artifact.version == version]

    if not artifacts:
        raise ArtifactNotFoundError(name)

    if len(artifacts) > 1:
        raise ArtifactAmbiguousError(
            name=name,
            artifacts=artifacts,
        )

    return artifacts[0]


def get_remote_artifacts(
    remote_name: str,
    project: str | None = None,
    artifact_type: str | None = None,
    name: str | None = None,
    experiment: str | None = None,
    model: str | None = None,
    since: timedelta | None = None,
    config_filters: list[ConfigFilter] | None = None,
    config_any_filters: list[ConfigFilter] | None = None,
) -> list[RemoteArtifact]:
    artifacts = discover_remote_artifacts(remote_name)

    filtered: list[RemoteArtifact] = []

    for artifact in artifacts:
        metadata = artifact.metadata

        promoted_at: datetime | None = None
        promoted_at_raw = metadata.get("promoted_at")

        if promoted_at_raw:
            try:
                promoted_at = datetime.fromisoformat(promoted_at_raw)
            except ValueError:
                pass

        if not matches_text(artifact.project, project):
            continue

        if not matches_text(artifact.artifact_type, artifact_type):
            continue

        if not matches_text(artifact.name, name):
            continue

        if not matches_text(
            metadata.get("experiment"),
            experiment,
        ):
            continue

        if not matches_text(
            metadata.get("model"),
            model,
        ):
            continue

        if not is_since(promoted_at, since):
            continue

        filtered.append(artifact)

    if filtered or config_any_filters:
        artifacts = filter_remote_artifacts_by_config(
            artifacts,
            filters=config_filters or [],
            any_filters=config_any_filters or [],
        )

    return filtered


def get_remote_artifact(
    remote_name: str,
    name: str,
    project: str | None = None,
    version: str | None = None,
) -> RemoteArtifact:
    """Resolve one remote artifact exactly."""

    artifacts = get_remote_artifacts(
        remote_name=remote_name,
        project=project,
    )

    matches = [
        artifact
        for artifact in artifacts
        if artifact.name == name and (version is None or artifact.version == version)
    ]

    if not matches:
        raise RemoteArtifactNotFoundError(
            name=name,
            remote_name=remote_name,
        )

    if len(matches) > 1:
        raise RemoteArtifactAmbiguousError(
            name=name,
            remote_name=remote_name,
            artifacts=matches,
        )

    return matches[0]
