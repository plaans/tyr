from importlib import import_module
from typing import List
import warnings

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

    configs: List[PlannerConfig] = []
    for p in content:
        config = PlannerConfig(**p)
        # Check if planner with upf_engine is actually available
        if config.upf_engine is not None:
            try:
                module_name, class_name = config.upf_engine.rsplit(".", 1)
                module = import_module(module_name)
                planner_class = getattr(module, class_name)
                # Try to instantiate the planner to check if it's really available
                planner_class()
            except (ImportError, ModuleNotFoundError, AttributeError) as e:
                warnings.warn(
                    f"Planner '{config.name}' not available: {e}",
                    ImportWarning,
                    stacklevel=2,
                )
                continue
        configs.append(config)
    return configs


def get_all_planners() -> List[Planner]:
    """
    Returns:
        List[Planner]: All planners defined in `tyr.configuration` module.
    """
    return [Planner(c) for c in get_all_planner_configs()]


__all__ = ["get_all_planners", "get_all_planner_configs"]
