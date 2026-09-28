import typer

from phd_artifacts.cli.artifacts import app as artifacts_app
from phd_artifacts.cli.init import init
from phd_artifacts.cli.projects import app as projects_app
from phd_artifacts.cli.promote import promote
from phd_artifacts.cli.runs import app as runs_app

app = typer.Typer(
    name="phd-artifact",
    help="Manage research artifacts across projects and machines.",
)

app.add_typer(
    projects_app,
    name="project",
)

app.add_typer(
    runs_app,
    name="run",
)

app.add_typer(
    artifacts_app,
    name="artifact",
)

app.command()(promote)


@app.callback()
def main():
    pass


@app.command()
def version():
    """Show the current version."""
    typer.echo("phd-artifacts 0.1.0")


app.command()(init)
