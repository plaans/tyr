from typing import List

from tyr.metrics.metric import Metric
from tyr.metrics.metrics.coverage import CoverageMetric
from tyr.metrics.metrics.quality_score import QualityScoreMetric
from tyr.planners.model.result import PlannerResult


class RelativeQualityScoreMetric(Metric):
    """A metric to evaluate the quality score of a planner relatively to its coverage."""

    def abbrev(self) -> str:
        return "RS"

    # pylint: disable=protected-access
    def _evaluate(
        self, results: List[PlannerResult], all_results: List[PlannerResult]
    ) -> float:
        cov = CoverageMetric()._evaluate(results, all_results)
        if cov == 0:
            return self.max_value()
        qs = QualityScoreMetric()._evaluate(results, all_results)
        return (1 - qs / cov) * 100
