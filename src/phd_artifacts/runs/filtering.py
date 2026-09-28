from datetime import timedelta

from phd_artifacts.core.filtering import is_since, matches_text
from phd_artifacts.runs.models import Run


def filter_runs(
    runs: list[Run],
    experiment: str | None = None,
    model: str | None = None,
    checkpoints_only: bool = False,
    since: timedelta | None = None,
) -> list[Run]:
    """Filter runs by their metadata."""

    return [
        run
        for run in runs
        if matches_text(run.experiment, experiment)
        and matches_text(run.model, model)
        and (not checkpoints_only or run.has_checkpoints)
        and is_since(
            run.created_at or run.modified_at,
            since,
        )
    ]
