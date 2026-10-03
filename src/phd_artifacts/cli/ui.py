from collections.abc import Generator
from contextlib import contextmanager

import questionary
import typer
from rich.console import Console
from rich.status import Status

from phd_artifacts.cli.theme import (
    QUESTIONARY_COMMON,
    QUESTIONARY_SELECT,
    RICH_THEME,
)

console = Console(theme=RICH_THEME)


class Activity:
    def __init__(self, status: Status):
        self._status = status

    def update(self, message: str) -> None:
        self._status.update(f"[info]{message}[/info]")


@contextmanager
def activity(message: str) -> Generator[Activity]:
    with console.status(
        f"[info]{message}[/info]",
        spinner="dots",
    ) as status:
        yield Activity(status)


def select(
    message: str,
    choices: list[questionary.Choice],
) -> object:
    result = questionary.select(
        message,
        choices=choices,
        **QUESTIONARY_SELECT,
    ).ask()

    if result is None:
        raise typer.Exit(0)

    return result


def checkbox(
    message: str,
    choices: list[questionary.Choice],
) -> list[object]:
    result = questionary.checkbox(
        message,
        choices=choices,
        instruction="Space to select, Enter to confirm",
        **QUESTIONARY_SELECT,
    ).ask()

    if result is None:
        raise typer.Exit(0)

    return result


def confirm(
    message: str,
    default: bool = True,
) -> bool:
    result = questionary.confirm(
        message,
        default=default,
        **QUESTIONARY_COMMON,
    ).ask()

    if result is None:
        raise typer.Exit(0)

    return bool(result)


def text(
    message: str,
    default: str = "",
) -> str:
    result = questionary.text(
        message,
        default=default,
        **QUESTIONARY_COMMON,
    ).ask()

    if result is None:
        raise typer.Exit(0)

    return result
