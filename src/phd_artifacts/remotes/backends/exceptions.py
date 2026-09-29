class BackendError(Exception):
    """Base exception for remote backend operations."""


class UnsupportedBackendError(BackendError):
    def __init__(
        self,
        backend_type: str,
        supported: list[str],
    ):
        self.backend_type = backend_type
        self.supported = supported

        supported_text = ", ".join(supported)

        super().__init__(
            f"Unsupported remote backend '{backend_type}'. Supported backends: {supported_text}"
        )
