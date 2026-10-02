from phd_artifacts.artifacts.models import Artifact, RemoteArtifact


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


class RemoteArtifactNotFoundError(ArtifactError):
    def __init__(
        self,
        name: str,
        remote_name: str,
    ):
        self.name = name
        self.remote_name = remote_name

        super().__init__(f"Artifact '{name}' not found on remote '{remote_name}'.")


class RemoteArtifactAmbiguousError(ArtifactError):
    def __init__(
        self,
        name: str,
        remote_name: str,
        artifacts: list[RemoteArtifact],
    ):
        self.name = name
        self.remote_name = remote_name
        self.artifacts = artifacts

        super().__init__(
            f"Artifact '{name}' has multiple matching versions on remote '{remote_name}'."
        )
