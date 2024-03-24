from typing import List

from tyr.metrics.metric import Metric
from tyr.planners.model.result import PlannerResult, PlannerResultStatus


class CoverageMetric(Metric):
    """A metric to evaluate the coverage of a planner."""

    def _evaluate(
        self,
        results: List[PlannerResult],
        all_results: List[PlannerResult],
    ) -> float:
        """Evaluate the performance of a planner."""
        if len(results) == 0:
            return 0
        return (
            len([r for r in results if r.status == PlannerResultStatus.SOLVED])
            / len(results)
            * 100
        )


__all__ = ["CoverageMetric"]
