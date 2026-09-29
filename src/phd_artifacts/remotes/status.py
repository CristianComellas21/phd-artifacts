from dataclasses import dataclass
from enum import StrEnum, auto


class RemoteStatus(StrEnum):
    MISSING = auto()
    UP_TO_DATE = auto()
    DIFFERENT = auto()


@dataclass
class RemoteComparison:
    status: RemoteStatus
