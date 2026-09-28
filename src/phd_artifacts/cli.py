import typer

app = typer.Typer(
    name="phd-artifact",
    help="Manage research artifacts across projects and machines.",
)


@app.callback()
def main():
    """Manage research artifacts across projects and machines."""
    pass


@app.command()
def version():
    """Show the current version."""
    typer.echo("phd-artifacts 0.1.0")