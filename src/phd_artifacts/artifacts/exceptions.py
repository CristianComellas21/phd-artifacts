from phd_artifacts.artifacts.models import Artifact


class ArtifactError(Exception):
    """Base exception for artifact operations."""


class ArtifactNotFoundError(ArtifactError):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Artifact '{name}' not found.")


class ArtifactAmbiguousError(ArtifactError):
    def __init__(
        self,
        name: str,
        artifacts: list[Artifact],
    ):
        self.name = name
        self.artifacts = artifacts

        super().__init__(f"Multiple artifacts found for '{name}'.")


class RemoteArtifactConflictError(ArtifactError):
    def __init__(
        self,
        name: str,
        remote_name: str,
    ):
        self.name = name
        self.remote_name = remote_name

        super().__init__(
            f"Artifact '{name}' already exists on remote "
            f"'{remote_name}' but differs from the local copy. "
            "Use --force to overwrite it."
        )
