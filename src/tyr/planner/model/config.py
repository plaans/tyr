from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class PlannerConfig:
    """Represents the configuration of a planner."""

    name: str
    problems: Dict[str, str]
