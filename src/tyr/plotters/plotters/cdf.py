from typing import List, Tuple

import plotly.graph_objects as go

from tyr.planners.model.config import RunningMode
from tyr.planners.model.result import PlannerResult
from tyr.plotters.plotter import Plotter


# pylint: disable = use-dict-literal
class CdfPlotter(Plotter):
    """
    A plotter to visualize the performance of a planner using
    a Cumulative Distribution Function (CDF) plot.
    """

    def _data(self, data: List[PlannerResult]) -> Tuple[List[float], List[float]]:
        """Extract the data to plot."""
        # pylint: disable = duplicate-code

        times = sorted(
            [
                float(r.computation_time or r.config.timeout)
                for r in data
                if r.running_mode == RunningMode.ONESHOT
            ]
        )
        return (
            times,
            list(i / len(times) for i in range(1, len(times) + 1)),
        )

    def update_layout(self, fig: go.Figure) -> None:
        """Update the layout of the figure."""
        fig.update_layout(
            title="Cumulative Distribution Function (CDF) Plot",
            xaxis=dict(
                title="Computation Time (seconds)",
            ),
            yaxis=dict(
                title="Instance Solved (%)",
            ),
        )


__all__ = ["CdfPlotter"]
