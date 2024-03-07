from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest
from unified_planning.plans import Plan, PlanKind
from unified_planning.io import PDDLReader

from tests.utils import ModelTest
from tyr import Lazy, ProblemInstance


class TestProblemInstance(ModelTest):
    # ============================================================================ #
    #                                    Getters                                   #
    # ============================================================================ #

    def get_default_attributes(self) -> Dict[str, Any]:
        return {
            "_uid": "05",
            "_domain": self.domain(),
            "_versions": dict(),
        }

    def get_instance(self) -> ProblemInstance:
        return ProblemInstance(self.domain(), "05")

    def domain(self):
        if not hasattr(self, "_domain"):
            self._domain = MagicMock()
            self._domain.name = "mockdomain"
        return self._domain

    @pytest.fixture()
    def problem(self, request):
        def build_version():
            folder = Path(__file__).parent.parent / "fixtures/pddl"
            return PDDLReader().parse_problem(
                (folder / "domain.pddl").as_posix(),
                (folder / "instance-01.pddl").as_posix(),
            )

        problem = self.get_instance()
        problem._versions = {"base": Lazy(build_version)}

        def teardown():
            problem._versions = {"base": Lazy(build_version)}

        request.addfinalizer(teardown)
        yield problem

    @staticmethod
    @pytest.fixture()
    def plan():
        yield "(move robot0 place0 place1)"

    @staticmethod
    @pytest.fixture()
    def timed_plan():
        yield "0.0: (move robot0 place0 place1) [15.0]"

    # ============================================================================ #
    #                                     Tests                                    #
    # ============================================================================ #

    def test_get_name(self, problem: ProblemInstance):
        expected = "mockdomain:05"
        assert problem.name == expected

    def test_is_empty(self, problem: ProblemInstance):
        problem._versions.clear()
        assert problem.is_empty

    def test_is_not_empty(self, problem: ProblemInstance):
        assert not problem.is_empty

    def test_add_version(self, problem: ProblemInstance):
        problem._versions.clear()
        version = MagicMock()
        problem.add_version("version", version)
        assert problem.versions == {"version": version}

    # ============================= Get plan quality ============================= #

    def test_get_quality_of_plan_without_metric(
        self, problem: ProblemInstance, plan: str
    ):
        orig_version = problem.versions["base"].value_factory()

        def build_version():
            orig_version.clear_quality_metrics()
            return orig_version

        problem._versions = {"base": Lazy(build_version)}
        result = problem.get_quality_of_plan(plan)
        assert result is None

    def test_get_quality_of_plan_multiple_metrics(
        self, problem: ProblemInstance, plan: str
    ):
        orig_version = problem.versions["base"].value_factory()

        def build_version():
            orig_version._metrics *= 2
            return orig_version

        problem._versions = {"base": Lazy(build_version)}

        with pytest.raises(ValueError):
            problem.get_quality_of_plan(plan)

    def test_get_quality_minimum_makespan(self, problem: ProblemInstance, plan: str):
        metric = MagicMock()
        metric.is_minimize_makespan.return_value = True
        problem.versions["base"].value._metrics = [metric]
        with patch.object(problem, "_get_makespan_of_plan") as mock_get_makespan:
            expected = mock_get_makespan.return_value
            result = problem.get_quality_of_plan(plan)
            assert result == expected

    def test_get_unknown_quality_of_plan(self, problem: ProblemInstance, plan: str):
        metric = MagicMock()
        metric.is_minimize_makespan.return_value = False
        problem.versions["base"].value._metrics = [metric]
        problem.get_quality_of_plan(plan)
        problem.domain.get_quality_of_plan.assert_called_once()

    def test_get_makespan_of_plan_time_triggered_plan(self, problem):
        plan = MagicMock(spec=Plan)
        plan.kind = PlanKind.TIME_TRIGGERED_PLAN
        plan.timed_actions = [
            (0, "action1", 2),
            (2, "action2", 6),
            (8, "action3", None),
        ]
        assert problem._get_makespan_of_plan(plan) == 8.0

    def test_get_makespan_of_plan_sequential_plan(self, problem):
        plan = MagicMock(spec=Plan)
        plan.kind = PlanKind.SEQUENTIAL_PLAN
        plan.actions = ["action1", "action2", "action3"]
        assert problem._get_makespan_of_plan(plan) == 3

    def test_get_makespan_of_plan_schedule(self, problem):
        plan = MagicMock(spec=Plan)
        plan.kind = PlanKind.SCHEDULE
        plan.activities = {Mock(end="1"), Mock(end="2"), Mock(end="3")}
        plan.assignment = {"1": 2.5, "2": 3.0, "3": 1.5}
        assert problem._get_makespan_of_plan(plan) == 3.0

    def test_get_makespan_of_plan_unknown(self, problem):
        plan = MagicMock(spec=Plan)
        plan.kind = "unknown"
        assert problem._get_makespan_of_plan(plan) is None
