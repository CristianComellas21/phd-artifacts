from pathlib import PurePosixPath

from phd_artifacts.core.config import load_config, save_config
from phd_artifacts.remotes.backends.registry import get_backend
from phd_artifacts.remotes.entries import RemoteEntry
from phd_artifacts.remotes.exceptions import RemoteNotFoundError
from phd_artifacts.remotes.models import Remote


def add_remote(
    name: str,
    remote_type: str,
    target: str,
) -> Remote:
    config = load_config()

    remotes = config.setdefault("remotes", {})

    if name in remotes:
        raise ValueError(f"Remote '{name}' already exists.")

    get_backend(remote_type)

    remotes[name] = {
        "type": remote_type,
        "target": target,
    }

    save_config(config)

    return Remote(
        name=name,
        type=remote_type,
        target=target,
    )


def remove_remote(name: str) -> None:
    config = load_config()

    remotes = config.get("remotes", {})

    if name not in remotes:
        raise RemoteNotFoundError(
            name=name,
            available=sorted(remotes),
        )

    del remotes[name]

    save_config(config)


def get_remote(name: str) -> Remote:
    config = load_config()

    remotes = config.get("remotes", {})
    data = remotes.get(name)

    if data is None:
        raise RemoteNotFoundError(
            name=name,
            available=sorted(remotes),
        )

    return Remote(
        name=name,
        type=data["type"],
        target=data["target"],
    )


def list_remotes() -> list[Remote]:
    config = load_config()

    remotes = []

    for name, data in config.get("remotes", {}).items():
        remotes.append(
            Remote(
                name=name,
                type=data["type"],
                target=data["target"],
            )
        )

    return sorted(remotes, key=lambda remote: remote.name)


def check_remote(name: str) -> Remote:
    remote = get_remote(name)

    backend = get_backend(remote.type)
    backend.check(remote)

    return remote


def list_remote(
    name: str,
    path: str = "",
) -> list[RemoteEntry]:
    remote = get_remote(name)
    backend = get_backend(remote.type)

    remote_path = _parse_remote_path(path)

    return backend.list(
        remote=remote,
        remote_path=remote_path,
    )


def _parse_remote_path(path: str) -> PurePosixPath:
    remote_path = PurePosixPath(path)

    if remote_path.is_absolute():
        raise ValueError("Remote path must be relative to the configured target.")

    if ".." in remote_path.parts:
        raise ValueError("Remote path cannot contain '..'.")

    return remote_path
