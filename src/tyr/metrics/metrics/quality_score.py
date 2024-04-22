from typing import List

from tyr.metrics.metric import Metric
from tyr.planners.model.result import PlannerResult, PlannerResultStatus


class QualityScoreMetric(Metric):
    """A metric to evaluate the quality score of a planner."""

    def abbrev(self) -> str:
        return "QS"

    def _evaluate(
        self,
        results: List[PlannerResult],
        all_results: List[PlannerResult],
    ) -> float:
        """Evaluate the performance of a planner."""
        if len(results) == 0:
            return 0
        total = self.min_value()
        for result in results:
            same_instances = [r for r in all_results if r.problem == result.problem]
            best_quality = min(
                float("inf") if r.plan_quality is None else r.plan_quality
                for r in same_instances
            )
            quality = result.plan_quality
            if result.status != PlannerResultStatus.SOLVED:
                total += 0
            elif quality is None:
                # Redundant with SOLVED but needed for typing and security
                total += 0
            elif quality == best_quality:
                total += 1
            else:
                total += best_quality / quality
        return total / len(results) * 100


__all__ = ["QualityScoreMetric"]
