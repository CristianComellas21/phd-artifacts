from pathlib import Path, PurePosixPath
from typing import Protocol

from phd_artifacts.remotes.entries import RemoteEntry
from phd_artifacts.remotes.models import Remote
from phd_artifacts.remotes.status import RemoteComparison


class RemoteBackend(Protocol):
    name: str

    def get_target(
        self,
        remote: Remote,
        remote_path: PurePosixPath,
    ) -> str: ...

    def check(self, remote: Remote) -> None:
        """Check that the remote is correctly configured and accessible."""
        ...

    def list(
        self,
        remote: Remote,
        remote_path: PurePosixPath,
    ) -> list[RemoteEntry]: ...

    def push(
        self,
        remote: Remote,
        source: Path,
        remote_path: PurePosixPath,
    ) -> str: ...

    def compare(
        self,
        remote: Remote,
        source: Path,
        remote_path: PurePosixPath,
    ) -> RemoteComparison: ...
