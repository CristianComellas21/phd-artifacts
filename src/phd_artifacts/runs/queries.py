from datetime import timedelta
from pathlib import Path

from phd_artifacts.projects.service import resolve_project
from phd_artifacts.runs.discovery import discover_runs
from phd_artifacts.runs.exceptions import (
    RunAmbiguousError,
    RunNotFoundError,
)
from phd_artifacts.runs.filtering import filter_runs
from phd_artifacts.runs.models import Run


def get_runs(
    project: str | None = None,
    experiment: str | None = None,
    model: str | None = None,
    checkpoints_only: bool = False,
    since: timedelta | None = None,
    include_tests: bool = False,
) -> list[Run]:
    """Get runs matching the requested filters."""

    project_name, project_config = resolve_project(project)

    runs = discover_runs(
        Path(project_config["logs"]),
        project_name=project_name,
        include_tests=include_tests,
    )

    return filter_runs(
        runs,
        experiment=experiment,
        model=model,
        checkpoints_only=checkpoints_only,
        since=since,
    )


def get_run(
    run_id: str,
    project: str | None = None,
    include_tests: bool = True,
) -> Run:
    """Resolve exactly one run by ID."""

    runs = get_runs(
        project=project,
        include_tests=include_tests,
    )

    matches = [run for run in runs if run.id == run_id]

    if not matches:
        raise RunNotFoundError(run_id)

    if len(matches) > 1:
        raise RunAmbiguousError(
            run_id,
            matches,
        )

    return matches[0]
