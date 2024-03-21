from math import log10
from typing import List

from tyr.metrics.metric import Metric
from tyr.planners.model.result import PlannerResult, PlannerResultStatus


class AgileScoreMetric(Metric):
    """A metric to evaluate the agile score of a planner."""

    def abbrev(self) -> str:
        return "AS"

    def max_value(self) -> float:
        return 1

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

        total = 0.0
        for result in results:
            computation_time = result.computation_time
            timeout = result.config.timeout
            if result.status != PlannerResultStatus.SOLVED:
                total += 0
            elif computation_time is None:
                # Redundant with SOLVED but needed for typing and security
                total += 0
            elif computation_time < 1:
                total += 1
            elif computation_time > timeout:
                total += 0
            else:
                total += 1 - log10(computation_time) / log10(timeout)
        score = total / len(results)
        if score == 1:
            return "1"
        return f"{score:.2f}"


__all__ = ["AgileScoreMetric"]
