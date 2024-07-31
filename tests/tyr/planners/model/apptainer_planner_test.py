from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, Mock, patch

import pytest
from unified_planning.engines.results import PlanGenerationResultStatus

from tyr.planners.model.apptainer_planner import ApptainerPlanner


class MockPlanner(ApptainerPlanner):
    def _get_apptainer_file_name(self):
        return "file.sif"


@pytest.fixture(scope="function")
def planner():
    yield MockPlanner()


class TestApptainerPlanner:
    def test_get_cmd(self, planner: MockPlanner):
        file = Path(__file__).parent / "file.sif"
        domain = "/tmp/domain.pddl"  # nosec: B108
        problem = "/tmp/problem.pddl"  # nosec: B108
        plan = "/tmp/plan.txt"  # nosec: B108
        expected = f"apptainer run -H /tmp -C {file} {domain} {problem} {plan}"
        result = planner._get_cmd(domain, problem, plan)
        assert result == expected.split()

    def test_get_anytime_cmd(self, planner: MockPlanner):
        planner = MockPlanner()
        file = Path(__file__).parent / "file.sif"
        domain = "/tmp/domain.pddl"  # nosec: B108
        problem = "/tmp/problem.pddl"  # nosec: B108
        plan = "/tmp/plan.txt"  # nosec: B108
        expected = f"apptainer run -H /tmp -C {file} {domain} {problem} {plan}"
        result = planner._get_anytime_cmd(domain, problem, plan)
        assert result == expected.split()

    @patch("tyr.planners.model.apptainer_planner.TyrPDDLPlanner._plan_from_str")
    def test_get_plan_from_str(self, super_mock: Mock, planner: MockPlanner):
        problem = MagicMock()
        get_item_named = MagicMock()
        plan_str = "f\n==>\n5 act1 var1 var2\n64 act2 var3\n9 act3 var4 var5 var6\nroot5 64 9\n"
        expected = "(act1 var1 var2)\n(act2 var3)\n(act3 var4 var5 var6)"
        assert planner._plan_found is None
        planner._plan_from_str(problem, plan_str, get_item_named)
        super_mock.assert_called_once_with(problem, expected, get_item_named)
        assert planner._plan_found is True

    @pytest.mark.parametrize("found", [True, False], ids=["found", "not_found"])
    @pytest.mark.parametrize("retval", [0, 1], ids=["ok", "error"])
    @pytest.mark.parametrize("plan", [MagicMock(), None], ids=["plan", "no_plan"])
    def test_result_status_solved(
        self,
        planner: MockPlanner,
        found: bool,
        retval: int,
        plan: Optional[MagicMock],
    ):
        problem = MagicMock()
        planner._plan_found = found
        assert (
            planner._result_status(problem, plan, retval)
            == PlanGenerationResultStatus.SOLVED_SATISFICING
        ) == (found and plan is not None)

    @pytest.mark.parametrize("found", [True, False], ids=["found", "not_found"])
    @pytest.mark.parametrize("retval", [0, 1], ids=["ok", "error"])
    @pytest.mark.parametrize("plan", [MagicMock(), None], ids=["plan", "no_plan"])
    def test_result_status_unsolvable(
        self,
        planner: MockPlanner,
        found: bool,
        retval: int,
        plan: Optional[MagicMock],
    ):
        problem = MagicMock()
        planner._plan_found = found
        assert (
            planner._result_status(problem, plan, retval)
            == PlanGenerationResultStatus.UNSOLVABLE_INCOMPLETELY
        ) == (retval == 0 and (not found or plan is None))

    @pytest.mark.parametrize("found", [True, False], ids=["found", "not_found"])
    @pytest.mark.parametrize("retval", [0, 1], ids=["ok", "error"])
    @pytest.mark.parametrize("plan", [MagicMock(), None], ids=["plan", "no_plan"])
    def test_result_status_error(
        self,
        planner: MockPlanner,
        found: bool,
        retval: int,
        plan: Optional[MagicMock],
    ):
        problem = MagicMock()
        planner._plan_found = found
        assert (
            planner._result_status(problem, plan, retval)
            == PlanGenerationResultStatus.INTERNAL_ERROR
        ) == (retval != 0 and (not found or plan is None))
