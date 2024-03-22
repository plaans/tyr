from typing import List, Tuple

import plotly.graph_objects as go

from tyr.planners.model.config import RunningMode
from tyr.planners.model.result import PlannerResult, PlannerResultStatus
from tyr.plotters.plotter import Plotter


# pylint: disable = use-dict-literal
class SurvivalPlotter(Plotter):
    """A plotter to visualize the performance of a planner using a survival plot."""

    def _data(self, data: List[PlannerResult]) -> Tuple[List[float], List[float]]:
        """Extract the data to plot."""
        times = sorted(
            [
                float(r.computation_time or r.config.timeout)
                for r in data
                if r.status == PlannerResultStatus.SOLVED
                and r.running_mode == RunningMode.ONESHOT
            ]
        )
        return (
            [sum(times[: i + 1]) for i in range(len(times))],
            list(range(1, len(times) + 1)),
        )

    def update_layout(self, fig: go.Figure) -> None:
        """Update the layout of the figure."""
        fig.update_layout(
            title="Survival Plot",
            xaxis=dict(
                title="Computation Time (seconds)",
                type="log",
            ),
            yaxis=dict(
                title="# Instances",
            ),
        )


__all__ = ["SurvivalPlotter"]
