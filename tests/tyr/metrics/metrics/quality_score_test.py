from unittest.mock import MagicMock

import pytest

from tyr.metrics.metrics.quality_score import QualityScoreMetric
from tyr.planners.model.config import SolveConfig
from tyr.planners.model.result import PlannerResult, PlannerResultStatus


def planner_result(status_name: str, quality: float):
    return PlannerResult(
        "foo",
        "bar",
        MagicMock(),
        getattr(PlannerResultStatus, status_name.upper()),
        SolveConfig(1, 1, 5, False, False),
        MagicMock(),
        quality,
        MagicMock(),
    )


class TestAgileScoreMetric:
    def test_abbrev(self):
        assert QualityScoreMetric().abbrev() == "QS"

    @pytest.mark.parametrize(
        "quality, expected",
        [
            (3, 1),
            (4, 0.75),
            (5, 0.6),
            (6, 0.5),
        ],
    )
    @pytest.mark.parametrize("status", PlannerResultStatus)
    def test_quality_score_single_result(self, quality, expected, status):
        if status != PlannerResultStatus.SOLVED:
            expected = (
                "-"
                if status
                in [
                    PlannerResultStatus.NOT_RUN,
                    PlannerResultStatus.UNSUPPORTED,
                    PlannerResultStatus.ERROR,
                ]
                else "0.00"
            )
        else:
            expected = f"{expected*100:.2f}" if expected != 1 else "100"
        results = [planner_result(status.name, quality)]
        all_results = results + [planner_result("solved", 3)]
        result = QualityScoreMetric().evaluate(results, all_results)
        assert result == expected

    def test_quality_score_multiple_results(self):
        results = [planner_result("solved", i) for i in range(3, 7)]
        all_results = results + [planner_result("solved", 3)]
        result = QualityScoreMetric().evaluate(results, all_results)
        expected = sum([1, 0.75, 0.6, 0.5]) / 4
        assert result == f"{expected*100:.2f}"

    def test_quality_score_empty_results(self):
        results = []
        result = QualityScoreMetric().evaluate(results, results)
        assert result == "-"

    def test_quality_score_skip_not_run_unsupported_error(self):
        results = [
            planner_result("solved", 0.5),
            planner_result("unsupported", 0.5),
            planner_result("not_run", 0.5),
            planner_result("error", 0.5),
        ]
        expected = "100"
        result = QualityScoreMetric().evaluate(results, results)
        assert result == expected
