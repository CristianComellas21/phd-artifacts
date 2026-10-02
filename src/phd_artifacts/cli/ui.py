from typing import TypeVar

import questionary
from rich.console import Console

from phd_artifacts.cli.theme import (
    QUESTIONARY_DEFAULTS,
    RICH_THEME,
)

T = TypeVar("T")

console = Console(theme=RICH_THEME)


def select(
    message: str,
    choices: list[questionary.Choice],
) -> T | None:
    return questionary.select(
        message,
        choices=choices,
        **QUESTIONARY_DEFAULTS,
    ).ask()


def checkbox(
    message: str,
    choices: list[questionary.Choice],
) -> list[T] | None:
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
