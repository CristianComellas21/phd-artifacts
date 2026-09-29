from phd_artifacts.core.config import load_config, save_config
from phd_artifacts.remotes.backends.registry import get_backend
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
        raise KeyError(f"Remote '{name}' not found.")

    del remotes[name]

    save_config(config)


def get_remote(name: str) -> Remote:
    config = load_config()

    data = config.get("remotes", {}).get(name)

    if data is None:
        raise KeyError(f"Remote '{name}' not found.")

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
