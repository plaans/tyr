from tyr.plotters.plotter import Plotter


class FakePlotter(Plotter):
    """A fake plotter to test the Plotter class."""

    def _data(self, data):
        pass

    def update_layout(self, fig):
        pass
