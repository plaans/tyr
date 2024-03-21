from math import log10
from unittest.mock import MagicMock

import pytest

from tyr.metrics.metrics.agile_score import AgileScoreMetric
from tyr.planners.model.config import SolveConfig
from tyr.planners.model.result import PlannerResult, PlannerResultStatus


def planner_result(status_name: str, computation_time: float):
    return PlannerResult(
        "foo",
        MagicMock(),
        MagicMock(),
        getattr(PlannerResultStatus, status_name.upper()),
        SolveConfig(1, 1, 5, False, False),
        computation_time,
        MagicMock(),
        MagicMock(),
    )


class TestAgileScoreMetric:
    @pytest.mark.parametrize(
        "computation_time, expected",
        [
            (0, 1),
            (0.5, 1),
            (1, 1),
            (2, 1 - log10(2) / log10(5)),
            (3, 1 - log10(3) / log10(5)),
            (4, 1 - log10(4) / log10(5)),
            (5, 0),
            (6, 0),
        ],
    )
    @pytest.mark.parametrize("status", PlannerResultStatus)
    def test_agile_score_single_result(self, computation_time, expected, status):
        if status != PlannerResultStatus.SOLVED:
            expected = 0
        results = [planner_result(status.name, computation_time)]
        result = AgileScoreMetric().evaluate(results)
        assert result == expected

    def test_agile_score_multiple_results(self):
        results = [planner_result("solved", i) for i in range(7)]
        result = AgileScoreMetric().evaluate(results)
        expected = (
            sum(
                [
                    1,
                    1,
                    1 - log10(2) / log10(5),
                    1 - log10(3) / log10(5),
                    1 - log10(4) / log10(5),
                    0,
                    0,
                ]
            )
            / 7
        )
        assert result == expected

    def test_agile_score_empty_results(self):
        results = []
        result = AgileScoreMetric().evaluate(results)
        assert result == 0

    def test_agile_score_skip_not_run_unsupported_error(self):
        results = [
            planner_result("solved", 0.5),
            planner_result("unsupported"),
            planner_result("not_run"),
            planner_result("error"),
        ]
        expected = 1
        result = AgileScoreMetric().evaluate(results)
        assert result == expected
