from pathlib import Path
from typing import List

import yaml

from tyr.planner.model.config import PlannerConfig


def get_all_planner_configs() -> List[PlannerConfig]:
    """
    Returns:
        List[PlannerConfig]: All planner configs defined in `tyr.configuration` module.
    """
    import tyr.configuration as config_module  # pylint: disable=import-outside-toplevel

    config_file = (Path(config_module.__path__[0]) / "planners.yaml").resolve()
    with open(config_file, "r", encoding="utf-8") as file:
        return [PlannerConfig(p) for p in yaml.safe_load(file)]
