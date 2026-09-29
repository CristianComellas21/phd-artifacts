from phd_artifacts.remotes.backends.base import RemoteBackend
from phd_artifacts.remotes.backends.rclone import RcloneBackend

_BACKENDS: dict[str, RemoteBackend] = {
    "rclone": RcloneBackend(),
}


def get_backend(backend_type: str) -> RemoteBackend:
    try:
        return _BACKENDS[backend_type]
    except KeyError:
        supported = ", ".join(sorted(_BACKENDS))

        raise ValueError(
            f"Unsupported remote type '{backend_type}'. Supported types: {supported}"
        ) from None


def get_supported_backend_types() -> list[str]:
    return sorted(_BACKENDS)
