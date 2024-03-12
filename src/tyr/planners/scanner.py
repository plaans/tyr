from typing import List

from tyr.configuration.loader import load_config
from tyr.planners.model.config import PlannerConfig
from tyr.planners.model.planner import Planner


def get_all_planner_configs() -> List[PlannerConfig]:
    """
    Returns:
        List[PlannerConfig]: All planner configs defined in `tyr.configuration` module.
    """
    if (content := load_config("planners")) is None:
        return []
    return [PlannerConfig(**p) for p in content]


def get_all_planners() -> List[Planner]:
    """
    Returns:
        List[Planner]: All planners defined in `tyr.configuration` module.
    """
    return [Planner(c) for c in get_all_planner_configs()]


__all__ = ["get_all_planners", "get_all_planner_configs"]
