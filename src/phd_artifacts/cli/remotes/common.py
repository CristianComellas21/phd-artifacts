from typing import cast

import questionary
import typer

from phd_artifacts.cli.ui import select
from phd_artifacts.remotes import list_remotes
from phd_artifacts.remotes.models import Remote


def resolve_remote_name(
    remote_name: str | None,
    auto_select_single: bool = True,
) -> str:
    if remote_name is not None:
        return remote_name

    remotes = list_remotes()

    if not remotes:
        raise typer.BadParameter("No remotes configured.")

    remotes = sorted(
        remotes,
        key=lambda remote: remote.name,
    )

    if len(remotes) == 1 and auto_select_single:
        return remotes[0].name

    selected = select(
        "Select remote:",
        [
            questionary.Choice(
                title=remote.name,
                value=remote,
            )
            for remote in remotes
        ],
    )

    return cast(Remote, selected).name
