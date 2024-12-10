from typing import List, Optional

from tyr.metrics.metric import Metric
from tyr.planners.model.config import RunningMode
from tyr.planners.model.result import PlannerResult, PlannerResultStatus


def _extract_first_quality(result: PlannerResult) -> Optional[float]:
    candidates = list(
        filter(lambda x: x.running_mode == RunningMode.ONESHOT, result.originals or [])
    )
    if len(candidates) == 0:
        return None
    if len(candidates) > 1:
        raise ValueError("Multiple ONESHOT plans found for the same problem")
    return candidates[0].plan_quality


class FirstQualityScoreMetric(Metric):
    """
    A metric to evaluate the quality score of a planner
    on its first plan compared to all other plans.
    """

    def abbrev(self) -> str:
        return "FQS"

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
            best_quality: float = min(  # type: ignore
                float("inf")
                if _extract_first_quality(r) is None
                or r.status != PlannerResultStatus.SOLVED
                else _extract_first_quality(r)
                for r in same_instances
            )
            quality = _extract_first_quality(result)
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

    def keep_best_result(self, results):
        return min(
            results,
            key=lambda r: _extract_first_quality(r)
            if _extract_first_quality(r) is not None
            and r.status == PlannerResultStatus.SOLVED
            else float("inf"),
        )


__all__ = ["FirstQualityScoreMetric"]
