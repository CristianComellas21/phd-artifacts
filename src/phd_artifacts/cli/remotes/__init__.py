import typer

from phd_artifacts.cli.remotes.add import add
from phd_artifacts.cli.remotes.list import list_remote_configs
from phd_artifacts.cli.remotes.remove import remove

app = typer.Typer(
    help="Manage remote artifact stores.",
)

app.command("add")(add)
app.command("list")(list_remote_configs)
app.command("remove")(remove)
