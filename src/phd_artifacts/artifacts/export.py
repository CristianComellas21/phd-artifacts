import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from phd_artifacts.projects.models import ProjectConfig


@dataclass
class ExportResult:
    output_dir: Path
    files: list[Path]


def resolve_project_python(
    project_root: Path,
    project_config: ProjectConfig,
) -> str:
    python_executable = project_config.get("python")

    if python_executable is None:
        return "python"

    path = Path(python_executable).expanduser()

    if not path.is_absolute():
        path = project_root / path

    path = path.resolve()

    if not path.is_file():
        raise RuntimeError(f"Project Python not found: {path}")

    return str(path)


def export_portable_weights(
    *,
    checkpoint_path: Path,
    artifact_path: Path,
    project_config: ProjectConfig,
) -> ExportResult | None:
    exporter = project_config.get("exporter")

    if not exporter:
        return None

    project_root = Path(project_config["root"]).resolve()

    exporter_path = (project_root / exporter).resolve()

    if not exporter_path.is_file():
        raise RuntimeError(f"Exporter not found: {exporter_path}")

    output_dir = (artifact_path / "portable").resolve()

    checkpoint_path = checkpoint_path.resolve()

    python_executable = resolve_project_python(
        project_root,
        project_config,
    )

    command = [
        python_executable,
        str(exporter_path),
        str(checkpoint_path),
        str(output_dir),
        *project_config.get("exporter_args", []),
    ]

    env = os.environ.copy()

    existing_pythonpath = env.get(
        "PYTHONPATH",
        "",
    )

    pythonpath_parts = [
        str(project_root),
    ]

    if existing_pythonpath:
        pythonpath_parts.append(existing_pythonpath)

    env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)

    result = subprocess.run(
        command,
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip()

        raise RuntimeError(
            "Portable export failed.\n"
            f"Project root: {project_root}\n"
            f"PYTHONPATH: {env['PYTHONPATH']}\n"
            f"Command: {' '.join(command)}\n\n"
            f"{message}"
        )

    files = sorted(path for path in output_dir.rglob("*") if path.is_file())

    if not files:
        raise RuntimeError("Exporter completed successfully but produced no files.")

    return ExportResult(
        output_dir=output_dir,
        files=files,
    )
