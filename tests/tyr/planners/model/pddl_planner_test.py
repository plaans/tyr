from typing import Any, List, Optional

import pytest
from unified_planning.engines.results import LogMessage, PlanGenerationResultStatus
from unified_planning.shortcuts import Problem

from tyr import TyrPDDLPlanner


class MockPlannerPlanner(TyrPDDLPlanner):
    def _get_cmd(  # pylint: disable = useless-parent-delegation
        self,
        domain_filename: str,
        problem_filename: str,
        plan_filename: str,
    ) -> List[str]:
        return super()._get_cmd(
            domain_filename,
            problem_filename,
            plan_filename,
        )

    def _get_anytime_cmd(  # pylint: disable = useless-parent-delegation
        self,
        domain_filename: str,
        problem_filename: str,
        plan_filename: str,
    ) -> List[str]:
        return super()._get_anytime_cmd(
            domain_filename,
            problem_filename,
            plan_filename,
        )

    def _result_status(
        self,
        problem: Problem,
        plan: Optional[Any],
        retval: int,
        log_messages: Optional[List[LogMessage]] = None,
    ) -> PlanGenerationResultStatus:
        return super()._result_status(problem, plan, retval, log_messages)


class TestTyrPDDLPlanner:
    @staticmethod
    @pytest.fixture()
    def planner():
        yield MockPlannerPlanner()

    def test_automatic_name(self, planner: TyrPDDLPlanner):
        assert planner.name == "mock-planner"

    def test_default_extension(self, planner: TyrPDDLPlanner):
        assert planner._file_extension() == "pddl"
