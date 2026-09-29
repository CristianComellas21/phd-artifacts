class RemoteError(Exception):
    """Base exception for remote operations."""


class RemoteNotFoundError(RemoteError):
    def __init__(
        self,
        name: str,
        available: list[str],
    ):
        self.name = name
        self.available = available

        if available:
            available_text = ", ".join(available)

            message = f"Remote '{name}' not found. Available remotes: {available_text}"
        else:
            message = f"Remote '{name}' not found. No remotes are configured."

        super().__init__(message)
