from pathlib import Path, PurePosixPath
from typing import Protocol

from phd_artifacts.remotes.models import Remote


class RemoteBackend(Protocol):
    name: str

    def check(self, remote: Remote) -> None:
        """Check that the remote is correctly configured and accessible."""
        ...

    def push(
        self,
        remote: Remote,
        source: Path,
        remote_path: PurePosixPath,
    ) -> str: ...
