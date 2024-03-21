from typing import List

from tyr.metrics.metric import Metric
from tyr.planners.model.result import PlannerResult, PlannerResultStatus


class CoverageMetric(Metric):
    """A metric to evaluate the coverage of a planner."""

    def evaluate(self, results: List[PlannerResult]) -> str:
        """Evaluate the performance of a planner."""
        results = [
            r
            for r in results
            if r.status
            not in [
                PlannerResultStatus.NOT_RUN,
                PlannerResultStatus.UNSUPPORTED,
                PlannerResultStatus.ERROR,
            ]
        ]

        if len(results) == 0:
            return "-"

        cov = (
            len([r for r in results if r.status == PlannerResultStatus.SOLVED])
            / len(results)
            * 100
        )
        if cov == 100:
            return "100"
        return f"{cov:.2f}"


__all__ = ["CoverageMetric"]
