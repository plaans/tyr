from unittest.mock import MagicMock

import pytest

from tyr.metrics.metrics.coverage import CoverageMetric
from tyr.metrics.metrics.quality_score import QualityScoreMetric
from tyr.metrics.metrics.relative_quality_score import RelativeQualityScoreMetric
from tyr.planners.model.result import PlannerResult


class TestRelativeQualityScoreMetric:
    def test_abbrev(self):
        metric = RelativeQualityScoreMetric()
        assert metric.abbrev() == "RS"

    @pytest.mark.parametrize(
        "cov, qs, expected",
        [(0, 50, 100), (30, 30, 0), (80, 40, 50), (20, 15, 25)],
    )
    def test_evaluate(self, cov, qs, expected):
        results = [MagicMock(spec=PlannerResult), MagicMock(spec=PlannerResult)]
        all_results = [MagicMock(spec=PlannerResult), MagicMock(spec=PlannerResult)]

        coverage_metric = CoverageMetric()
        quality_score_metric = QualityScoreMetric()

        coverage_metric._evaluate = MagicMock(return_value=cov)
        quality_score_metric._evaluate = MagicMock(return_value=qs)

        metric = RelativeQualityScoreMetric()
        assert metric._evaluate(results, all_results) == expected

        coverage_metric._evaluate.assert_called_once_with(results, all_results)
        if cov != 0:
            quality_score_metric._evaluate.assert_called_once_with(results, all_results)
        else:
            quality_score_metric._evaluate.assert_not_called()
