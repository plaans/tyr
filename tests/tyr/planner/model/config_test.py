from typing import Any, Dict

from tests.utils import ModelTest
from tyr import PlannerConfig


class TestPlannerConfig(ModelTest):
    def get_default_attributes(self) -> Dict[str, Any]:
        return {
            "_name": "upf-mock",
            "_problems": {"mockdomain": "base", "mockdomainbis": "base"},
        }

    def get_instance(self) -> PlannerConfig:
        return PlannerConfig(
            name="upf-mock",
            problems={"mockdomain": "base", "mockdomainbis": "base"},
        )

    def test_equality(self):
        config1 = PlannerConfig(
            **{
                "name": "upf-mock",
                "problems": {"mockdomain": "base", "mockdomainbis": "base"},
            }
        )
        config2 = PlannerConfig(
            **{
                "name": "upf-mock",
                "problems": {"mockdomain": "base", "mockdomainbis": "base"},
            }
        )
        config3 = PlannerConfig(
            **{
                "name": "upf-mock-2",
                "problems": {"mockdomain": "base", "mockdomainbis": "base"},
            }
        )
        config4 = PlannerConfig(
            **{
                "name": "upf-mock",
                "problems": {"mockdomain-2": "base", "mockdomainbis": "base"},
            }
        )
        config5 = {
            "name": "upf-mock",
            "problems": {"mockdomain": "base", "mockdomainbis": "base"},
        }
        configs = [config1, config2, config3, config4, config5]

        def match_idx(i, j):
            return i == j or (i in [0, 1] and j in [0, 1])

        for i, config_i in enumerate(configs):
            for j, config_j in enumerate(configs):
                assert (config_i == config_j) == match_idx(i, j)
                assert (config_i != config_j) == (not match_idx(i, j))
