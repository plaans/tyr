from unittest.mock import MagicMock

from tyr.metrics.metrics.coverage import CoverageMetric
from tyr.planners.model.result import PlannerResult, PlannerResultStatus


def planner_result(status_name: str):
    return PlannerResult(
        "foo",
        MagicMock(),
        MagicMock(),
        getattr(PlannerResultStatus, status_name.upper()),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )


class TestCoverageMetric:
    def test_coverage_metric(self):
        results = [
            planner_result("solved"),
            planner_result("unsolvable"),
            planner_result("timeout"),
            planner_result("memout"),
            planner_result("error"),
            planner_result("unsupported"),
            planner_result("not_run"),
        ]
        expected = f"{1 / (len(results)) * 100:.2f}"
        result = CoverageMetric().evaluate(results, results)
        assert result == expected

    def test_coverage_empty_results(self):
        results = []
        result = CoverageMetric().evaluate(results, results)
        assert result == "-"

    def test_coverage_skip_not_run_unsupported_error(self):
        results = [
            planner_result("solved"),
            planner_result("unsupported"),
            planner_result("not_run"),
            planner_result("error"),
        ]
        expected = "25.00"
        result = CoverageMetric().evaluate(results, results)
        assert result == expected
