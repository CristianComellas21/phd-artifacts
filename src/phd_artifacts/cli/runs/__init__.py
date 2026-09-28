import typer

from phd_artifacts.cli.runs.list import list_runs
from phd_artifacts.cli.runs.show import show_run

app = typer.Typer(
    help="Inspect experiment runs.",
)

app.command("list")(list_runs)
app.command("show")(show_run)
