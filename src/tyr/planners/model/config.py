from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict


@dataclass(frozen=True)
class PlannerConfig:
    """Represents the configuration of a planner."""

    name: str
    problems: Dict[str, str]
    env: Dict[str, str] = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(self.name) + hash(str(self.problems))


@dataclass(frozen=True)
class SolveConfig:
    """Represents the configuration of the solving process."""

    jobs: int
    memout: int
    timeout: int


class RunningMode(Enum):
    """Different mode to run planner resolutions."""

    ANYTIME = auto()
    ONESHOT = auto()
