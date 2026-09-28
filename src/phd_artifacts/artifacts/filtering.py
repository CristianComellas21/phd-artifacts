from datetime import datetime, timedelta

from phd_artifacts.artifacts.models import Artifact
from phd_artifacts.core.filtering import is_since, matches_text


def filter_artifacts(
    artifacts: list[Artifact],
    project: str | None = None,
    artifact_type: str | None = None,
    name: str | None = None,
    experiment: str | None = None,
    model: str | None = None,
    since: timedelta | None = None,
) -> list[Artifact]:
    """Filter promoted artifacts by their metadata."""

    filtered: list[Artifact] = []

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
