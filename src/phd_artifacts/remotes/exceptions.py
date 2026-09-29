class RemoteError(Exception):
    """Base exception for remote operations."""


class RemoteNotFoundError(RemoteError):
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Remote '{name}' not found.")
