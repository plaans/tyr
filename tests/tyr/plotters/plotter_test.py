import pytest

from tyr.plotters.plotter import Plotter


class FakePlotter(Plotter):
    def _plot(self, fig, data, color, symbol, planner, domain):
        pass


class TestPlotter:
    def test_is_abstract(self):
        with pytest.raises(TypeError):
            Plotter()

    def test_child_can_be_instantiated(self):
        FakePlotter()

    def test_is_singleton(self):
        assert FakePlotter() is FakePlotter()

    def test_name(self):
        class FakeComplexPlotter(Plotter):
            def evaluate(self, results):
                pass

        assert FakeComplexPlotter().name == "fake-complex"
