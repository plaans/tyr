from unittest.mock import patch

import pytest
from unified_planning.shortcuts import OneshotPlanner

import tests.integration.planners as planner_module
import tests.tyr.planners.fixtures.configuration as config_module
from tyr import Planner, get_all_planners, register_all_planners


class TestLoader:
    @patch("tyr.planners.planners")
    @patch("tyr.configuration")
    def test_register_all_planners_mocked(self, mocked_config, mocked_planners):
        mocked_planners.__path__ = planner_module.__path__
        mocked_planners.__name__ = planner_module.__name__
        mocked_config.__path__ = config_module.__path__
        register_all_planners()
        planners = get_all_planners()
        for planner in planners:
            OneshotPlanner(name=planner.name)

    @pytest.mark.parametrize(
        "planner", get_all_planners(), ids=lambda x: x.oneshot_name
    )
    def test_real_planner_upf_registration_oneshot(self, planner: Planner):
        # Check the planner is registered in unified planning
        register_all_planners()
        OneshotPlanner(name=planner.oneshot_name)

    @pytest.mark.parametrize(
        "planner", get_all_planners(), ids=lambda x: x.anytime_name
    )
    def test_real_planner_upf_registration_anytime(self, planner: Planner):
        # Check the planner is registered in unified planning
        register_all_planners()
        OneshotPlanner(name=planner.anytime_name)
