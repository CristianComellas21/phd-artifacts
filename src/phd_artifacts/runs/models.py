from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class Run:
    id: str
    path: Path
    relative_path: Path

    experiment: str | None
    model: str | None

    created_at: datetime | None
    modified_at: datetime

    has_checkpoints: bool
