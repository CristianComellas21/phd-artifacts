from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from phd_artifacts.artifacts.exceptions import CheckpointRoleNotFoundError


@dataclass
class Artifact:
    path: Path
    relative_path: Path
    project: str
    artifact_type: str
    name: str
    version: str
    metadata: dict

    def checkpoint_roles(self) -> list[str]:
        return list(self.metadata.get("checkpoints", {}))

    def checkpoint_relative_path(self, role: str) -> Path:
        checkpoints = self.metadata.get("checkpoints", {})

        if role not in checkpoints:
            raise CheckpointRoleNotFoundError(
                role=role,
                available=list(checkpoints),
            )

        return Path(checkpoints[role]["path"])

    def checkpoint_path(self, role: str) -> Path:
        return self.path / self.checkpoint_relative_path(role)

    def checkpoint_source(self, role: str) -> Path:
        checkpoints = self.metadata.get("checkpoints", {})

        if role not in checkpoints:
            raise CheckpointRoleNotFoundError(
                role=role,
                available=list(checkpoints),
            )

        return Path(checkpoints[role]["source"])


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
