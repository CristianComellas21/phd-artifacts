from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass
class RemoteEntry:
    name: str
    path: PurePosixPath
    is_dir: bool
    size: int | None = None
