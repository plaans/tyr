from tyr.plotters.plotter import Plotter


class FakePlotter(Plotter):
    """A fake plotter to test the Plotter class."""

    # pylint: disable = too-many-arguments
    def _plot(self, fig, data, color, symbol, planner, domain):
        pass

    def update_layout(self, fig):
        pass
