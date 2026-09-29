class ProjectError(Exception):
    """Base exception for project operations."""


class ProjectNotFoundError(ProjectError):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Project '{name}' not found.")


class ProjectNotResolvedError(ProjectError):
    def __init__(self):
        super().__init__(
            "Current directory does not belong to a registered project. Specify one with --project."
        )
