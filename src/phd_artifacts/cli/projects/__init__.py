import typer

from phd_artifacts.cli.projects.add import add
from phd_artifacts.cli.projects.configure import configure
from phd_artifacts.cli.projects.current import current
from phd_artifacts.cli.projects.list import list_projects_command
from phd_artifacts.cli.projects.remove import remove

app = typer.Typer(
    help="Manage research projects.",
)

app.command("add")(add)
app.command("list")(list_projects_command)
app.command("remove")(remove)
app.command("current")(current)
app.command("configure")(configure)
