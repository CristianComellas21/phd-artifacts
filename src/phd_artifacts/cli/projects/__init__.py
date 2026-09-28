import typer

from phd_artifacts.cli.projects.add import add
from phd_artifacts.cli.projects.current import current
from phd_artifacts.cli.projects.list import list_projects
from phd_artifacts.cli.projects.remove import remove


app = typer.Typer(
    help="Manage research projects.",
)

app.command("add")(add)
app.command("list")(list_projects)
app.command("remove")(remove)
app.command("current")(current)