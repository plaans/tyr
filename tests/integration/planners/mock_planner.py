from typing import List

from tests.integration.planners.fake_planner import FakePlannerPlanner


# pylint: disable=too-many-ancestors, duplicate-code
class MockPlannerPlanner(FakePlannerPlanner):
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
