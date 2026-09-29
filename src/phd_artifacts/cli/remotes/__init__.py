import typer

from phd_artifacts.cli.remotes.add import add
from phd_artifacts.cli.remotes.check import check
from phd_artifacts.cli.remotes.list import list_remote_configs
from phd_artifacts.cli.remotes.ls import ls
from phd_artifacts.cli.remotes.remove import remove
from phd_artifacts.cli.remotes.tree import tree

app = typer.Typer(
    help="Manage remote artifact stores.",
)

app.command("add")(add)
app.command("list")(list_remote_configs)
app.command("remove")(remove)
app.command("check")(check)
app.command("ls")(ls)
app.command("tree")(tree)
