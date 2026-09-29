from phd_artifacts.runs.models import Run


class RunError(Exception):
    pass


class RunNotFoundError(RunError):
    def __init__(self, run_id: str):
        self.run_id = run_id
        super().__init__(f"Run '{run_id}' not found.")


class RunAmbiguousError(RunError):
    def __init__(self, run_id: str, runs: list[Run]):
        self.run_id = run_id
        self.runs = runs
        super().__init__(f"Multiple runs found for '{run_id}'.")
