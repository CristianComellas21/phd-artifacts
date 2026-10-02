from typing import NotRequired, TypedDict


class ProjectConfig(TypedDict):
    root: str
    logs: str
    workspace_artifacts: str
    python: NotRequired[str]
    exporter: NotRequired[str]
    exporter_args: NotRequired[list[str]]
