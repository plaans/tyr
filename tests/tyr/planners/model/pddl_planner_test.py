from typing import Any, List

import pytest
from unified_planning.engines.results import LogMessage, PlanGenerationResultStatus
from unified_planning.shortcuts import Problem

from tyr import TyrPDDLPlanner


class MockPlannerPlanner(TyrPDDLPlanner):
    def _get_cmd(
        self, domain_filename: str, problem_filename: str, plan_filename: str
    ) -> List[str]:
        return super()._get_cmd(domain_filename, problem_filename, plan_filename)

    def _result_status(
        self,
        problem: Problem,
        plan: Any | None,
        retval: int,
        log_messages: List[LogMessage] | None = None,
    ) -> PlanGenerationResultStatus:
        return super()._result_status(problem, plan, retval, log_messages)


class TestTyrPDDLPlanner:
    @staticmethod
    @pytest.fixture()
    def planner():
        yield MockPlannerPlanner()

    def test_automatic_name(self, planner: TyrPDDLPlanner):
        assert planner.name == "mock-planner"
