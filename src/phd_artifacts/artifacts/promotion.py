import platform
import shutil
from datetime import UTC, datetime
from pathlib import Path

import tomli_w

from phd_artifacts.artifacts.export import export_portable_weights
from phd_artifacts.artifacts.models import CheckpointSelection
from phd_artifacts.artifacts.verification import compute_sha256
from phd_artifacts.core.config import load_config
from phd_artifacts.core.progress import NULL_PROGRESS, ProgressReporter
from phd_artifacts.projects.service import get_project
from phd_artifacts.runs.models import Run


def get_checkpoint_store(project_name: str) -> Path:
    config = load_config()

    artifact_root = Path(config["artifact_root"])

    return artifact_root / project_name / "checkpoints"


def get_artifact_version(run: Run) -> str:
    timestamp = run.created_at or run.modified_at

    return f"{timestamp:%Y%m%d_%H%M%S}_{run.id}"


def promote_checkpoints(
    run: Run,
    checkpoints: list[CheckpointSelection],
    name: str,
    no_export: bool = False,
    progress: ProgressReporter = NULL_PROGRESS,
) -> Path:
    """Promote run checkpoints into the persistent artifact store."""

    project_name = run.project
    project_config = get_project(project_name)

    store = get_checkpoint_store(project_name)
    version = get_artifact_version(run)

    destination = store / name / version

    if destination.exists():
        raise FileExistsError(f"Artifact already exists: {destination}")

    progress.update("Preparing artifact")

    destination.mkdir(parents=True)

    try:
        checkpoints_dir = destination / "checkpoints"
        checkpoints_dir.mkdir()

        checkpoint_metadata: dict[str, dict] = {}

        for selection in checkpoints:
            role = selection.role
            source_checkpoint = selection.path

            checkpoint_destination = checkpoints_dir / f"{role}.ckpt"

            progress.update(f"Copying checkpoint '{role}'")

            shutil.copy2(
                source_checkpoint,
                checkpoint_destination,
            )

            portable_files: list[dict] = []

            if not no_export:
                progress.update(f"Exporting portable weights for '{role}'")

                export_result = export_portable_weights(
                    checkpoint_path=checkpoint_destination,
                    artifact_path=destination,
                    project_config=project_config,
                    output_subdir=f"portable/{role}",
                )

                if export_result is not None:
                    progress.update(f"Computing portable checksums for '{role}'")
                    for path in export_result.files:
                        portable_files.append(
                            {
                                "path": path.relative_to(destination).as_posix(),
                                "size_bytes": (path.stat().st_size),
                                "sha256": compute_sha256(path),
                            }
                        )

            progress.update(f"Computing checksums for '{role}'")

            checkpoint_metadata[role] = {
                "path": checkpoint_destination.relative_to(destination).as_posix(),
                "source": str(source_checkpoint),
                "size_bytes": (checkpoint_destination.stat().st_size),
                "sha256": compute_sha256(checkpoint_destination),
            }

            if portable_files:
                checkpoint_metadata[role]["portable_files"] = portable_files

        hydra_dir = run.path / ".hydra"

        for filename in (
            "config.yaml",
            "overrides.yaml",
            "hydra.yaml",
        ):
            source = hydra_dir / filename

            if source.is_file():
                progress.update("Copying Hydra configuration")

                shutil.copy2(
                    source,
                    destination / filename,
                )

        metadata = {
            "version": 2,
            "name": name,
            "project": project_name,
            "type": "checkpoint",
            "run_id": run.id,
            "experiment": run.experiment or "",
            "model": run.model or "",
            "source_host": platform.node(),
            "promoted_at": datetime.now(UTC).isoformat(),
            "source": {
                "run": str(run.path),
            },
            "checkpoints": checkpoint_metadata,
        }

        if run.created_at:
            metadata["run_created_at"] = run.created_at.isoformat()

        if not no_export and "exporter" in project_config:
            metadata["export"] = {
                "status": "ok",
                "exporter": project_config["exporter"],
            }

        progress.update("Writing metadata")

        with (destination / "metadata.toml").open("wb") as file:
            tomli_w.dump(
                metadata,
                file,
            )

        progress.update("Finalizing artifact")

    except Exception:
        shutil.rmtree(
            destination,
            ignore_errors=True,
        )
        raise

    return destination
