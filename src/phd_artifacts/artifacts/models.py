from dataclasses import dataclass
from pathlib import Path, PurePosixPath


@dataclass
class Artifact:
    path: Path
    relative_path: Path
    project: str
    artifact_type: str
    name: str
    version: str
    metadata: dict


@dataclass
class RemoteArtifact:
    remote: str
    path: PurePosixPath
    project: str
    artifact_type: str
    name: str
    version: str
    metadata: dict


@dataclass(frozen=True)
class CheckpointSelection:
    role: str
    path: Path
