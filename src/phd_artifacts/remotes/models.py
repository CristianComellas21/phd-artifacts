from dataclasses import dataclass


@dataclass
class Remote:
    name: str
    type: str
    target: str
