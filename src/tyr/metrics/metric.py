import re
from typing import List

from tyr.patterns import AbstractSingletonMeta
from tyr.patterns.abstract import Abstract
from tyr.patterns.singleton import Singleton
from tyr.planners.model.result import PlannerResult, PlannerResultStatus


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

    def min_value(self) -> float:
        """The minimum value of the metric."""
        return 0

    def max_value(self) -> float:
        """The maximum value of the metric."""
        return 100

    def _filter_results(self, results: List[PlannerResult]) -> List[PlannerResult]:
        return [
            r
            for r in results
            if r.status
            not in [
                PlannerResultStatus.NOT_RUN,
                PlannerResultStatus.UNSUPPORTED,
                PlannerResultStatus.ERROR,
            ]
        ]

    def _evaluate(
        self,
        results: List[PlannerResult],
        all_results: List[PlannerResult],
    ) -> float:
        """Evaluate the performance of a planner."""
        raise NotImplementedError

    def evaluate(
        self,
        results: List[PlannerResult],
        all_results: List[PlannerResult],
    ) -> str:
        """
        Evaluate the performance of a planner.

        Args:
            results: The results to evaluate.
            all_results: All the results containing the other planners and domains.
        """
        results, all_results = tuple(map(self._filter_results, (results, all_results)))
        if len(results) == 0:
            return "-"
        value = self._evaluate(results, all_results)
        if value == self.max_value():
            return str(int(value))
        return f"{value:.2f}"

    def best_across_domains(
        self,
        results: List[PlannerResult],
        all_results: List[PlannerResult],
    ) -> str:
        """Return the best performance across the domains for a planner."""
        domains = set(r.problem.domain.name for r in results)
        best = self.min_value()
        for domain in domains:
            dom_results = [r for r in results if r.problem.domain.name == domain]
            value = self.evaluate(dom_results, all_results)
            best = max(best, float(value) if value != "-" else self.min_value())
            if best == self.max_value():
                break
        return (
            "-"
            if best == self.min_value()
            else f"{best:.2f}"
            if best != self.max_value()
            else str(int(best))
        )

    def best_across_planners(
        self,
        results: List[PlannerResult],
        all_results: List[PlannerResult],
    ) -> str:
        """Return the best performance across the planners for a domain."""
        planners = set(r.planner_name for r in results)
        best = self.min_value()
        for planner in planners:
            planner_results = [r for r in results if r.planner_name == planner]
            value = self.evaluate(planner_results, all_results)
            best = max(best, float(value) if value != "-" else self.min_value())
            if best == self.max_value():
                break
        return (
            "-"
            if best == self.min_value()
            else f"{best:.2f}"
            if best != self.max_value()
            else str(int(best))
        )


__all__ = ["Metric"]
