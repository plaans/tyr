from unittest.mock import MagicMock

import pytest

from tyr.metrics.metric import Metric
from tyr.planners.model.result import PlannerResult, PlannerResultStatus


class FakeMetric(Metric):
    def evaluate(self, results, all_results):
        solved = len([r for r in results if r.status == PlannerResultStatus.SOLVED])
        total = len(results)
        return f"{solved / total * 100:.2f}"


def planner_result(status_name: str, domain_name="zoo", planner_name="zoo"):
    problem = MagicMock()
    problem.domain.name = domain_name
    return PlannerResult(
        planner_name,
        problem,
        MagicMock(),
        getattr(PlannerResultStatus, status_name.upper()),
        MagicMock(),
        MagicMock(),
        MagicMock(),
        MagicMock(),
    )


class TestMetric:
    def test_is_abstract(self):
        with pytest.raises(TypeError):
            Metric()

    def test_child_can_be_instantiated(self):
        FakeMetric()

    def test_is_singleton(self):
        assert FakeMetric() is FakeMetric()

    def test_name(self):
        class FakeComplexMetric(Metric):
            def evaluate(self, results, all_results):
                pass

        assert FakeComplexMetric().name == "fake-complex"

    def test_abbrev(self):
        class FakeComplexMetric(Metric):
            def evaluate(self, results, all_results):
                pass

        assert FakeComplexMetric().abbrev() == "fak"

    def test_best_across_domains(self):
        results = [
            planner_result("solved", domain_name="bar"),
            planner_result("solved", domain_name="bar"),
            planner_result("unsolvable", domain_name="bar"),
            planner_result("unsolvable", domain_name="bar"),
            planner_result("solved", domain_name="foo"),
            planner_result("unsolvable", domain_name="foo"),
            planner_result("unsolvable", domain_name="foo"),
            planner_result("unsolvable", domain_name="foo"),
        ]
        expected = "50.00"
        result = FakeMetric().best_across_domains(results, results)
        assert result == expected

    def test_best_across_domains_max_value(self):
        results = [
            planner_result("solved", domain_name="bar"),
            planner_result("solved", domain_name="bar"),
            planner_result("solved", domain_name="foo"),
            planner_result("unsolvable", domain_name="foo"),
        ]
        expected = "100"
        result = FakeMetric().best_across_domains(results, results)
        assert result == expected

    def test_best_across_planners(self):
        results = [
            planner_result("solved", planner_name="bar"),
            planner_result("solved", planner_name="bar"),
            planner_result("unsolvable", planner_name="bar"),
            planner_result("unsolvable", planner_name="bar"),
            planner_result("solved", planner_name="foo"),
            planner_result("unsolvable", planner_name="foo"),
            planner_result("unsolvable", planner_name="foo"),
            planner_result("unsolvable", planner_name="foo"),
        ]
        expected = "50.00"
        result = FakeMetric().best_across_planners(results, results)
        assert result == expected

    def test_best_across_planners_max_value(self):
        results = [
            planner_result("solved", planner_name="bar"),
            planner_result("solved", planner_name="bar"),
            planner_result("solved", planner_name="foo"),
            planner_result("unsolvable", planner_name="foo"),
        ]
        expected = "100"
        result = FakeMetric().best_across_planners(results, results)
        assert result == expected
