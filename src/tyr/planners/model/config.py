from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, Optional


@dataclass(frozen=True)
class PlannerConfig:
    """Represents the configuration of a planner."""

    name: str
    problems: Dict[str, str]
    env: Dict[str, str] = field(default_factory=dict)
    anytime_name: Optional[str] = None
    oneshot_name: Optional[str] = None
    upf_engine: Optional[str] = None

    def __hash__(self) -> int:
        return hash(self.name) + hash(str(self.problems))


@dataclass(frozen=True)
class SolveConfig:
    """Represents the configuration of the solving process."""

    jobs: int
    memout: int
    timeout: int
    timeout_offset: int
    db_only: bool
    no_db_load: bool
    no_db_save: bool


class RunningMode(Enum):
    """Different mode to run planner resolutions."""

    ANYTIME = auto()
    ONESHOT = auto()


__all__ = ["PlannerConfig", "SolveConfig", "RunningMode"]
