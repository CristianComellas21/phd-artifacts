from dataclasses import dataclass
from pathlib import Path


@dataclass
class Artifact:
    path: Path
    relative_path: Path
    project: str
    artifact_type: str
    name: str
    version: str
    metadata: dict
