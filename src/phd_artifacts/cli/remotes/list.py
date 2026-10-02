from rich.table import Table

from phd_artifacts.cli.ui import console
from phd_artifacts.remotes import list_remotes


def list_remote_configs():
    """List configured artifact remotes."""

    remotes = list_remotes()

    if not remotes:
        console.print("No remotes configured.")
        return

    table = Table(
        "Name",
        "Type",
        "Target",
    )

    for remote in remotes:
        table.add_row(
            remote.name,
            remote.type,
            remote.target,
        )

    console.print(table)
