import re
from typing import List

from tyr.patterns import AbstractSingletonMeta
from tyr.patterns.abstract import Abstract
from tyr.patterns.singleton import Singleton
from tyr.planners.model.result import PlannerResult


# pylint: disable = too-few-public-methods
class Metric(Abstract, Singleton, metaclass=AbstractSingletonMeta):
    """A metric to evaluate the performance of a planner."""

    def __init__(self) -> None:
        super().__init__()
        base_name = self.__class__.__name__[:-6]
        self._name = re.sub(r"([A-Z])", r"-\1", base_name).lower().lstrip("-")

    @property
    def name(self) -> str:
        """The name of the metric."""
        return self._name

    def abbrev(self) -> str:
        """The abbreviation of the name of the metric."""
        return self.name[:3]

    def evaluate(self, results: List[PlannerResult]) -> str:
        """Evaluate the performance of a planner."""
        raise NotImplementedError


__all__ = ["Metric"]
