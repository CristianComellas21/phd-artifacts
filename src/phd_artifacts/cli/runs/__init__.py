import typer

from phd_artifacts.cli.runs.list import list_runs

app = typer.Typer(
    help="Inspect experiment runs.",
)

app.command("list")(list_runs)
