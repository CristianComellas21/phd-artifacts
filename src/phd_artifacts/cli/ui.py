import questionary
from rich.console import Console

from phd_artifacts.cli.theme import (
    QUESTIONARY_DEFAULTS,
    RICH_THEME,
)

console = Console(theme=RICH_THEME)


def select(
    message: str,
    choices: list[questionary.Choice],
) -> object | None:
    return questionary.select(
        message,
        choices=choices,
        **QUESTIONARY_DEFAULTS,
    ).ask()


def checkbox(
    message: str,
    choices: list[questionary.Choice],
) -> list[object] | None:
    return questionary.checkbox(
        message,
        choices=choices,
        instruction="Space to select, Enter to confirm",
        **QUESTIONARY_DEFAULTS,
    ).ask()


def confirm(
    message: str,
    default: bool = True,
) -> bool:
    result = questionary.confirm(
        message,
        default=default,
        **QUESTIONARY_DEFAULTS,
    ).ask()

    return bool(result)


def text(
    message: str,
    default: str | None = None,
) -> str | None:
    return questionary.text(
        message,
        default=default or "",
        **QUESTIONARY_DEFAULTS,
    ).ask()
