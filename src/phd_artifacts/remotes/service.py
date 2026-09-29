from phd_artifacts.core.config import load_config, save_config
from phd_artifacts.remotes.models import Remote

SUPPORTED_REMOTE_TYPES = {"rclone"}


def add_remote(
    name: str,
    remote_type: str,
    target: str,
) -> Remote:
    config = load_config()

    remotes = config.setdefault("remotes", {})

    if name in remotes:
        raise ValueError(f"Remote '{name}' already exists.")

    if remote_type not in SUPPORTED_REMOTE_TYPES:
        raise ValueError(
            f"Unsupported remote type '{remote_type}'. "
            f"Supported types: {', '.join(sorted(SUPPORTED_REMOTE_TYPES))}"
        )

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
