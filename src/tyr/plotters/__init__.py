import sys
from . import cactus, survival
from .cactus import *
from .survival import *


def get_all_plotters():
    """
    Returns:
        List[Callable[[List[PlannerResult]], None]]: All plotters defined in `tyr.plotters` module.
    """
    return [getattr(sys.modules[__name__], name) for name in __all__[:-1]]


__all__ = cactus.__all__ + survival.__all__ + ["get_all_plotters"]
