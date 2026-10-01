from datetime import datetime, timedelta

from phd_artifacts.artifacts.discovery import (
    discover_artifacts,
    discover_remote_artifacts,
)
from phd_artifacts.artifacts.exceptions import ArtifactAmbiguousError, ArtifactNotFoundError
from phd_artifacts.artifacts.filtering import filter_artifacts
from phd_artifacts.artifacts.models import Artifact, RemoteArtifact
from phd_artifacts.core.filtering import is_since, matches_text


def get_artifacts(
    project: str | None = None,
    artifact_type: str | None = None,
    name: str | None = None,
    experiment: str | None = None,
    model: str | None = None,
    since: timedelta | None = None,
) -> list[Artifact]:
    """Get promoted artifacts matching the requested filters."""

    artifacts = discover_artifacts()

    return filter_artifacts(
        artifacts,
        project=project,
        artifact_type=artifact_type,
        name=name,
        experiment=experiment,
        model=model,
        since=since,
    )


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

    return filtered
