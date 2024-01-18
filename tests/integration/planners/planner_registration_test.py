import pytest
from unified_planning.shortcuts import OneshotPlanner

from tyr import Planner, get_all_planners


class TestPlannerRegistration:
    @pytest.mark.parametrize("planner", get_all_planners(), ids=lambda x: x.name)
    def test_real_planner_upf_registration(self, planner: Planner):
        # Check the planner is registered in unified planning
        OneshotPlanner(name=planner.name)
