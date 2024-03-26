from importlib import import_module
from pkgutil import walk_packages
from typing import List

from tyr.plotters.plotter import Plotter


def get_all_plotters() -> List[Plotter]:
    """
    Returns:
        List[Plotter]: All plotters defined in `tyr.plotters.plotters` module.
    """
    # pylint: disable=import-outside-toplevel, cyclic-import
    import tyr.plotters.plotters as plotter_module

    plotters = []

    for _, name, _ in walk_packages(plotter_module.__path__):
        module = import_module(f"{plotter_module.__name__}.{name}")
        for obj_name in dir(module):
            if obj_name.endswith("Plotter") and obj_name != "Plotter":
                obj = getattr(module, obj_name)
                if issubclass(obj, Plotter):
                    plotters.append(obj())

    return list(set(plotters))  # Remove duplicates


__all__ = ["get_all_plotters"]
