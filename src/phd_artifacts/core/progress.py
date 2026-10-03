from typing import Protocol


class ProgressReporter(Protocol):
    def update(self, message: str) -> None: ...


class NullProgressReporter:
    def update(self, message: str) -> None:
        pass


NULL_PROGRESS = NullProgressReporter()
