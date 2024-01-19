from tyr import PlannerConfig


class TestPlannerConfig:
    def test_hash(self):
        config1 = PlannerConfig(
            name="config1", problems={"a": "problem1", "b": "problem2"}
        )
        config2 = PlannerConfig(
            name="config1", problems={"a": "problem1", "b": "problem2"}
        )
        assert hash(config1) == hash(config2)

    def test_hash_not_equal(self):
        config1 = PlannerConfig(
            name="config1", problems={"a": "problem1", "b": "problem2"}
        )
        config2 = PlannerConfig(
            name="config2", problems={"c": "problem3", "d": "problem4"}
        )
        assert hash(config1) != hash(config2)
