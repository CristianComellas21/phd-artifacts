from datetime import timedelta
from typing import cast

import typer
from rich.table import Table

from phd_artifacts.artifacts import get_artifacts
from phd_artifacts.artifacts.models import Artifact, RemoteArtifact
from phd_artifacts.artifacts.queries import get_remote_artifacts
from phd_artifacts.cli.ui import activity, console
from phd_artifacts.core.config_filtering import ConfigFilter, parse_config_filters
from phd_artifacts.core.filtering import parse_duration
from phd_artifacts.remotes.backends.exceptions import UnsupportedBackendError
from phd_artifacts.remotes.exceptions import RemoteError


def _get_artifacts_for_list(
    *,
    project: str | None,
    artifact_type: str | None,
    name: str | None,
    experiment: str | None,
    model: str | None,
    since: timedelta | None,
    remote: str | None,
    config_filters: list[ConfigFilter],
    config_any_filters: list[ConfigFilter],
) -> list[Artifact] | list[RemoteArtifact]:
    if remote is None:
        return get_artifacts(
            project=project,
            artifact_type=artifact_type,
            name=name,
            experiment=experiment,
            model=model,
            since=since,
            config_filters=config_filters,
            config_any_filters=config_any_filters,
        )

    with activity(f"Reading artifacts from '{remote}'") as reporter:
        remote_artifacts = get_remote_artifacts(
            remote_name=remote,
            project=project,
            artifact_type=artifact_type,
            name=name,
            experiment=experiment,
            model=model,
            since=since,
            config_filters=config_filters,
            config_any_filters=config_any_filters,
            progress=reporter,
        )

    return remote_artifacts


def _print_empty_message(
    remote: str | None,
) -> None:
    if remote is None:
        console.print("No promoted artifacts found.")
        return

    console.print(f"No promoted artifacts found on remote '{remote}'.")


def _render_local_artifacts(
    artifacts: list[Artifact],
) -> None:
    table = Table(
        "Project",
        "Type",
        "Name",
        "Version",
    )

    for artifact in artifacts:
        table.add_row(
            artifact.project,
            artifact.artifact_type,
            artifact.name,
            artifact.version,
        )

    console.print(table)


def _render_remote_artifacts(
    artifacts: list[RemoteArtifact],
) -> None:
    table = Table(
        "Remote",
        "Project",
        "Type",
        "Name",
        "Version",
    )

    for artifact in artifacts:
        table.add_row(
            artifact.remote,
            artifact.project,
            artifact.artifact_type,
            artifact.name,
            artifact.version,
        )

    console.print(table)


def list_artifacts(
    project: str | None = typer.Option(
        None,
        "--project",
        "-p",
        help="Filter by project.",
    ),
    artifact_type: str | None = typer.Option(
        None,
        "--type",
        "-t",
        help="Filter by artifact type.",
    ),
    name: str | None = typer.Option(
        None,
        "--name",
        "-n",
        help="Filter by artifact name.",
    ),
    experiment: str | None = typer.Option(
        None,
        "--experiment",
        "-e",
        help="Filter by experiment name.",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        "-m",
        help="Filter by model name.",
    ),
    since: str | None = typer.Option(
        None,
        "--since",
        help="Show artifacts promoted within a duration such as 7d or 2w.",
    ),
    remote: str | None = typer.Option(
        None,
        "--remote",
        "-r",
        help="List artifacts stored on a remote instead of locally.",
    ),
    config: list[str] | None = typer.Option(
        None,
        "--config",
        help=(
            "Filter by config value using an exact path. "
            "Can be repeated. Quote expressions, e.g. "
            "--config 'dataset.fixed_variance=15'."
        ),
    ),
    config_any: list[str] | None = typer.Option(
        None,
        "--config-any",
        help=(
            "Filter by a config key found anywhere in the config. "
            "Can be repeated. Quote expressions, e.g. "
            "--config-any 'fixed_variance=15'."
        ),
    ),
):
    """List promoted artifacts."""

    try:
        since_delta = parse_duration(since) if since else None

        config_filters = parse_config_filters(config or [])

        config_any_filters = parse_config_filters(config_any or [])

    except ValueError as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None

    try:
        artifacts = _get_artifacts_for_list(
            project=project,
            artifact_type=artifact_type,
            name=name,
            experiment=experiment,
            model=model,
            since=since_delta,
            remote=remote,
            config_filters=config_filters,
            config_any_filters=config_any_filters,
        )

    except (
        RemoteError,
        UnsupportedBackendError,
        RuntimeError,
    ) as exc:
        console.print(f"[error]{exc}[/error]")
        raise typer.Exit(1) from None

    if not artifacts:
        _print_empty_message(remote)
        return

    if remote is None:
        _render_local_artifacts(cast(list[Artifact], artifacts))
    else:
        _render_remote_artifacts(cast(list[RemoteArtifact], artifacts))
