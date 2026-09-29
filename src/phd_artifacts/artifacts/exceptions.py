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
