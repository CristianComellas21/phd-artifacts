from pathlib import Path
import tomllib

import tomli_w
from platformdirs import user_config_dir


APP_NAME = "phd-artifacts"
CONFIG_FILENAME = "config.toml"


def get_config_dir() -> Path:
    return Path(user_config_dir(APP_NAME))


def get_config_path() -> Path:
    return get_config_dir() / CONFIG_FILENAME


def config_exists() -> bool:
    return get_config_path().exists()


def load_config() -> dict:
    path = get_config_path()

    if not path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {path}. "
            "Run 'phd-artifact init' first."
        )

    with path.open("rb") as f:
        return tomllib.load(f)


def save_config(config: dict) -> None:
    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("wb") as f:
        tomli_w.dump(config, f)


def create_config(artifact_root: Path) -> Path:
    artifact_root = artifact_root.expanduser().resolve()

    config = {
        "version": 1,
        "artifact_root": str(artifact_root),
        "projects": {},
    }

    save_config(config)

    return get_config_path()