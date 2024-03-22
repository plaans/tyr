from typing import List

import plotly.graph_objects as go

from tyr.planners.model.result import PlannerResult, PlannerResultStatus
from tyr.plotters.plotter import Plotter


# pylint: disable = use-dict-literal
class SurvivalPlotter(Plotter):
    """A plotter to visualize the performance of a planner using a survival plot."""

    # pylint: disable = too-many-arguments
    def _plot(
        self,
        fig: go.Figure,
        data: List[PlannerResult],
        color: str,
        symbol: str,
        planner: str,
        domain: str,
    ) -> None:
        """Plot the performance of a planner."""
        times = sorted(
            [
                float(r.computation_time or r.config.timeout)
                for r in data
                if r.status == PlannerResultStatus.SOLVED
            ]
        )
        fig.add_trace(
            go.Scatter(
                x=[sum(times[: i + 1]) for i in range(len(times))],
                y=list(range(1, len(times) + 1)),
                mode="lines+markers",
                line=dict(color=color, width=2),
                marker=dict(color=color, size=8, symbol=symbol),
                name=f"{planner} - {domain}",
            )
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
