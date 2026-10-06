import builtins
import json
import shutil
import subprocess
from pathlib import Path, PurePosixPath

from phd_artifacts.remotes.entries import RemoteEntry
from phd_artifacts.remotes.models import Remote
from phd_artifacts.remotes.status import RemoteComparison, RemoteStatus


class RcloneBackend:
    name = "rclone"

    def get_target(
        self,
        remote: Remote,
        remote_path: PurePosixPath,
    ) -> str:
        return self._join_target(
            remote.target,
            remote_path,
        )

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

    def pull(
        self,
        remote: Remote,
        remote_path: PurePosixPath,
        destination: Path,
    ) -> None:
        target = self.get_target(
            remote=remote,
            remote_path=remote_path,
        )

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        result = subprocess.run(
            [
                "rclone",
                "copy",
                target,
                str(destination),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()

            raise RuntimeError(f"Remote pull failed: {message}")

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

    def list(
        self,
        remote: Remote,
        remote_path: PurePosixPath,
    ) -> list[RemoteEntry]:
        self.check(remote)

        target = self.get_target(
            remote=remote,
            remote_path=remote_path,
        )

        result = subprocess.run(
            [
                "rclone",
                "lsjson",
                target,
                "--max-depth",
                "1",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()

            raise RuntimeError(f"Could not list remote path '{target}': {message}")

        data = json.loads(result.stdout)

        entries: list[RemoteEntry] = []

        for item in data:
            name = item["Name"]
            is_dir = item.get("IsDir", False)

            entries.append(
                RemoteEntry(
                    name=name,
                    path=remote_path / name,
                    is_dir=is_dir,
                    size=None if is_dir else item.get("Size"),
                )
            )

        entries.sort(
            key=lambda entry: (
                not entry.is_dir,
                entry.name.lower(),
            )
        )

        return entries

    def list_recursive(
        self,
        remote: Remote,
        remote_path: PurePosixPath,
        max_depth: int | None = None,
    ) -> builtins.list[RemoteEntry]:
        self.check(remote)

        target = self.get_target(
            remote=remote,
            remote_path=remote_path,
        )

        command = [
            "rclone",
            "lsjson",
            target,
            "--recursive",
        ]

        if max_depth is not None:
            command.extend(
                [
                    "--max-depth",
                    str(max_depth + 1),
                ]
            )

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()

            raise RuntimeError(f"Could not list remote path '{target}': {message}")

        data = json.loads(result.stdout)

        entries: builtins.list[RemoteEntry] = []

        for item in data:
            item_path = PurePosixPath(item["Path"])

            entries.append(
                RemoteEntry(
                    name=item["Name"],
                    path=remote_path / item_path,
                    is_dir=item.get("IsDir", False),
                    size=(None if item.get("IsDir", False) else item.get("Size")),
                )
            )

        return entries

    def read_text(
        self,
        remote: Remote,
        remote_path: PurePosixPath,
    ) -> str:
        target = self.get_target(
            remote=remote,
            remote_path=remote_path,
        )

        result = subprocess.run(
            [
                "rclone",
                "cat",
                target,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()

            raise RuntimeError(f"Could not read remote file '{target}': {message}")

        return result.stdout

    def write_text(
        self,
        remote: Remote,
        remote_path: PurePosixPath,
        text: str,
    ) -> None:
        target = self.get_target(
            remote=remote,
            remote_path=remote_path,
        )

        result = subprocess.run(
            ["rclone", "rcat", target],
            input=text,
            text=True,
            capture_output=True,
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or f"Failed to write remote file: {target}")

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
    def _list_remotes() -> builtins.list[str]:
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
