from pathlib import Path
from typing import List

import yaml

from tyr.planners.model.config import PlannerConfig
from tyr.planners.model.planner import Planner


def get_all_planner_configs() -> List[PlannerConfig]:
    """
    Returns:
        List[PlannerConfig]: All planner configs defined in `tyr.configuration` module.
    """
    import tyr.configuration as config_module  # pylint: disable=import-outside-toplevel

    config_file = (Path(config_module.__path__[0]) / "planners.yaml").resolve()
    with open(config_file, "r", encoding="utf-8") as file:
        content = yaml.safe_load(file)

    if content is None:
        return []
    return [PlannerConfig(**p) for p in content]


def get_all_planners() -> List[Planner]:
    """
    Returns:
        List[Planner]: All planners defined in `tyr.configuration` module.
    """
    return [Planner(c) for c in get_all_planner_configs()]


__all__ = ["get_all_planners", "get_all_planner_configs"]
