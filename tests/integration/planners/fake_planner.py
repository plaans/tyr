from typing import Any, List, Optional

from unified_planning.engines.results import (
    LogMessage,
    PlanGenerationResultStatus,
    Problem,
)

from tyr import TyrPDDLPlanner


class FakePlannerPlanner(TyrPDDLPlanner):
    """A fake planner used for tests."""

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
