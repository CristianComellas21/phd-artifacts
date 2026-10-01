import yaml

from phd_artifacts.core.config_filtering import (
    ConfigFilter,
    matches_config,
    matches_config_any,
)
from phd_artifacts.runs.models import Run


def load_run_config(
    run: Run,
) -> dict | None:
    """Load the resolved Hydra config for a run."""

    path = run.path / ".hydra" / "config.yaml"

    if not path.is_file():
        return None

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            config = yaml.safe_load(file)

    except (OSError, yaml.YAMLError):
        return None

    if not isinstance(config, dict):
        return None

    return config


def filter_runs_by_config(
    runs: list[Run],
    filters: list[ConfigFilter],
    any_filters: list[ConfigFilter] | None = None,
) -> list[Run]:
    """Filter runs using their resolved Hydra configurations."""

    if not filters and not any_filters:
        return runs

    matches: list[Run] = []

    for run in runs:
        config = load_run_config(run)

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

        matches.append(run)

    return matches
