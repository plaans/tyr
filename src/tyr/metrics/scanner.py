from importlib import import_module
from pkgutil import walk_packages
from typing import List

from tyr.metrics.metric import Metric


def get_all_metrics() -> List[Metric]:
    """
    Returns:
        List[Metric]: All metrics defined in `tyr.metrics.metrics` module.
    """
    # pylint: disable=import-outside-toplevel, cyclic-import
    import tyr.metrics.metrics as metric_module

    metrics = []

    for _, name, _ in walk_packages(metric_module.__path__):
        module = import_module(f"{metric_module.__name__}.{name}")
        for obj_name in dir(module):
            if obj_name.endswith("Metric") and obj_name != "Metric":
                obj = getattr(module, obj_name)
                if issubclass(obj, Metric):
                    metrics.append(obj())

    return list(set(metrics))  # Remove duplicates


__all__ = ["get_all_metrics"]
