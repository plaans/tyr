from math import log10
from unittest.mock import MagicMock

import pytest

from tyr.metrics.metrics.time_score import TimeScoreMetric
from tyr.planners.model.config import SolveConfig
from tyr.planners.model.result import PlannerResult, PlannerResultStatus


def planner_result(status_name: str, computation_time: float):
    return PlannerResult(
        "foo",
        MagicMock(),
        MagicMock(),
        getattr(PlannerResultStatus, status_name.upper()),
        SolveConfig(1, 1, 5, False, False, False),
        computation_time,
        MagicMock(),
        MagicMock(),
    )


class TestAgileScoreMetric:
    def test_abbrev(self):
        assert TimeScoreMetric().abbrev() == "TS"

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
        results = [planner_result(status.name, computation_time)]
        result = TimeScoreMetric().evaluate(results, results)
        assert result == expected

    def test_agile_score_multiple_results(self):
        results = [planner_result("solved", i) for i in range(7)]
        result = TimeScoreMetric().evaluate(results, results)
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
        assert result == f"{expected*100:.2f}"

    def test_agile_score_empty_results(self):
        results = []
        result = TimeScoreMetric().evaluate(results, results)
        assert result == "-"

    def test_agile_score_skip_not_run_unsupported_error(self):
        results = [
            planner_result("solved", 0.5),
            planner_result("unsupported", 0.5),
            planner_result("not_run", 0.5),
            planner_result("error", 0.5),
        ]
        expected = "100"
        result = TimeScoreMetric().evaluate(results, results)
        assert result == expected
