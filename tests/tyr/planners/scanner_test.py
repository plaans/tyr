from unittest.mock import patch

import tests.tyr.planners.fixtures.configuration as config_module
from tyr import Planner, PlannerConfig, get_all_planner_configs, get_all_planners


class TestScanner:
    @patch("tyr.configuration")
    def test_get_all_planner_configs_mocked(self, mocked_module):
        mocked_module.__path__ = config_module.__path__
        expected = [
            PlannerConfig(
                name="upf-mock",
                problems={"mockdomain": "base", "mockdomainbis": "base_2"},
            ),
            PlannerConfig(
                name="upf-mock-2",
                problems={"mockdomainter": "base", "mockdomainquad": "base_2"},
            ),
        ]
        result = get_all_planner_configs()
        assert result == expected

    def test_get_all_planner_configs_real(self):
        # Check no crash
        get_all_planner_configs()

    @patch("tyr.configuration")
    def test_get_all_planners_mocked(self, mocked_module):
        mocked_module.__path__ = config_module.__path__
        expected = [Planner(c) for c in get_all_planner_configs()]
        result = get_all_planners()
        assert set(result) == set(expected)

    def test_get_all_planners_real(self):
        # Check no crash
        get_all_planners()
