from unittest.mock import patch

import tests.tyr.planners.fixtures.configuration as config_module
from tyr import Planner, PlannerConfig, get_all_planner_configs, get_all_planners


class TestScanner:
    @patch("tyr.configuration")
    def test_get_all_planner_configs_mocked(self, mocked_module):
        mocked_module.__path__ = config_module.__path__
        expected = [
            PlannerConfig(
                name="fake-planner",
                problems={"mockdomain": "base", "mockdomainbis": "base_2"},
                env={},
            ),
            PlannerConfig(
                name="mock-planner",
                problems={"mockdomainter": "base", "mockdomainquad": "base_2"},
                env={"MY_ENV_PARAM": "bar", "MY_BOOL_PARAM": True},
            ),
        ]
        result = get_all_planner_configs()
        assert result == expected

    @patch("yaml.safe_load")
    def test_get_all_planner_configs_empty_file(self, mocked_yaml):
        mocked_yaml.return_value = None
        result = get_all_planner_configs()
        assert result == []

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
