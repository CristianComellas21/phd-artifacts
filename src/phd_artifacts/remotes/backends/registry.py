from phd_artifacts.remotes.backends.base import RemoteBackend
from phd_artifacts.remotes.backends.exceptions import UnsupportedBackendError
from phd_artifacts.remotes.backends.rclone import RcloneBackend

_BACKENDS: dict[str, RemoteBackend] = {
    "rclone": RcloneBackend(),
}


def get_backend(backend_type: str) -> RemoteBackend:
    try:
        return _BACKENDS[backend_type]
    except KeyError:
        raise UnsupportedBackendError(
            backend_type=backend_type,
            supported=get_supported_backend_types(),
        ) from None


def get_supported_backend_types() -> list[str]:
    return sorted(_BACKENDS)
