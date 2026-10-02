import typer

from phd_artifacts.cli.artifacts.list import list_artifacts
from phd_artifacts.cli.artifacts.pull import pull
from phd_artifacts.cli.artifacts.push import push
from phd_artifacts.cli.artifacts.show import show_artifact
from phd_artifacts.cli.artifacts.status import status
from phd_artifacts.cli.artifacts.verify import verify

app = typer.Typer(
    help="Manage promoted research artifacts.",
)

app.command("list")(list_artifacts)
app.command("show")(show_artifact)
app.command("verify")(verify)
app.command("push")(push)
app.command("pull")(pull)
app.command("status")(status)
