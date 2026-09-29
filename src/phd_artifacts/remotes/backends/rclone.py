import shutil
import subprocess
from pathlib import Path, PurePosixPath

from phd_artifacts.remotes.models import Remote
from phd_artifacts.remotes.status import RemoteComparison, RemoteStatus


class RcloneBackend:
    name = "rclone"

    def check(self, remote: Remote) -> None:
        self._check_available()

        remote_name = self._get_remote_name(remote.target)
        configured_remotes = self._list_remotes()

        if remote_name not in configured_remotes:
            raise RuntimeError(f"rclone remote '{remote_name}:' is not configured.")

        self._check_remote_access(remote_name)

    def push(
        self,
        remote: Remote,
        source: Path,
        remote_path: PurePosixPath,
    ) -> str:
        self.check(remote)

        destination = self._join_target(
            remote.target,
            remote_path,
        )

        result = subprocess.run(
            [
                "rclone",
                "copy",
                str(source),
                destination,
                "--progress",
            ]
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to push '{source}' to '{destination}'.")

        return destination

    def compare(
        self,
        remote: Remote,
        source: Path,
        remote_path: PurePosixPath,
    ) -> RemoteComparison:
        self.check(remote)

        destination = self._join_target(
            remote.target,
            remote_path,
        )

        if not self._exists(destination):
            return RemoteComparison(
                status=RemoteStatus.MISSING,
            )

        result = subprocess.run(
            [
                "rclone",
                "check",
                str(source),
                destination,
                "--one-way",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return RemoteComparison(
                status=RemoteStatus.UP_TO_DATE,
            )

        return RemoteComparison(
            status=RemoteStatus.DIFFERENT,
        )

    @staticmethod
    def _check_available() -> None:
        if shutil.which("rclone") is None:
            raise RuntimeError("rclone is not installed or not available in PATH.")

    @staticmethod
    def _get_remote_name(target: str) -> str:
        if ":" not in target:
            raise ValueError(
                f"Invalid rclone target '{target}'. Expected something like 'remote:path'."
            )

        return target.split(":", maxsplit=1)[0]

    @staticmethod
    def _list_remotes() -> list[str]:
        result = subprocess.run(
            ["rclone", "listremotes"],
            capture_output=True,
            text=True,
            check=True,
        )

        return [line.strip().rstrip(":") for line in result.stdout.splitlines() if line.strip()]

    @staticmethod
    def _check_remote_access(remote_name: str) -> None:
        target = f"{remote_name}:"

        result = subprocess.run(
            [
                "rclone",
                "lsd",
                target,
                "--max-depth",
                "1",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()

            raise RuntimeError(f"Could not access rclone remote '{target}': {message}")

    @staticmethod
    def _join_target(
        target: str,
        path: PurePosixPath,
    ) -> str:
        base = target.rstrip("/")

        if not path.parts:
            return base

        return f"{base}/{path.as_posix()}"

    @staticmethod
    def _exists(target: str) -> bool:
        result = subprocess.run(
            [
                "rclone",
                "lsf",
                target,
                "--max-depth",
                "1",
            ],
            capture_output=True,
            text=True,
        )

        return result.returncode == 0
