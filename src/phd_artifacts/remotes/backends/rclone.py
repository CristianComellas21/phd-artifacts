import shutil
import subprocess

from phd_artifacts.remotes.models import Remote


class RcloneBackend:
    name = "rclone"

    def check(self, remote: Remote) -> None:
        self._check_available()

        remote_name = self._get_remote_name(remote.target)
        configured_remotes = self._list_remotes()

        if remote_name not in configured_remotes:
            raise RuntimeError(f"rclone remote '{remote_name}:' is not configured.")

        self._check_remote_access(remote_name)

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
