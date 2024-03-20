import pytest

from tyr.metrics.metric import Metric


class TestMetric:
    def test_is_abstract(self):
        with pytest.raises(TypeError):
            Metric()

    def test_child_can_be_instantiated(self):
        class FakeMetric(Metric):
            def evaluate(self, results):
                pass

        FakeMetric()

    def test_is_singleton(self):
        class FakeMetric(Metric):
            def evaluate(self, results):
                pass

        assert FakeMetric() is FakeMetric()

    def test_name(self):
        class FakeComplexMetric(Metric):
            def evaluate(self, results):
                pass

        assert FakeComplexMetric().name == "fake-complex"
