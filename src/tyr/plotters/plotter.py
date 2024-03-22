import re
from typing import List, Tuple

import plotly.graph_objects as go
from plotly.colors import DEFAULT_PLOTLY_COLORS
from plotly.validators.scatter.marker import SymbolValidator

from tyr.patterns import AbstractSingletonMeta
from tyr.patterns.abstract import Abstract
from tyr.patterns.singleton import Singleton
from tyr.planners.model.result import PlannerResult


class Plotter(Abstract, Singleton, metaclass=AbstractSingletonMeta):
    """A plotter to visualize the performance of a planner."""

    def __init__(self) -> None:
        super().__init__()
        base_name = self.__class__.__name__[:-7]
        self._name = re.sub(r"([A-Z])", r"-\1", base_name).lower().lstrip("-")

    @property
    def name(self) -> str:
        """The name of the plotter."""
        return self._name

    def _data(self, data: List[PlannerResult]) -> Tuple[List[float], List[float]]:
        """Extract the data to plot."""
        raise NotImplementedError

    def plot(self, results: List[PlannerResult]) -> None:
        """Plot the performance of a planner."""
        planners = sorted(set(r.planner_name for r in results))
        domains = sorted(set(r.problem.domain.name for r in results))
        symbols = SymbolValidator().values
        fig = go.Figure()

        for i, planner in enumerate(planners):
            color = DEFAULT_PLOTLY_COLORS[i % len(DEFAULT_PLOTLY_COLORS)]
            for j, domain in enumerate(domains):
                symbol = symbols[(j * 12) % len(symbols) + 2]
                x, y = self._data(
                    [
                        r
                        for r in results
                        if r.planner_name == planner and r.problem.domain.name == domain
                    ]
                )
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y,
                        mode="lines+markers",
                        line=dict(color=color, width=2),
                        marker=dict(color=color, size=8, symbol=symbol),
                        name=f"{planner} - {domain}",
                    )
                )

        self.update_layout(fig)
        fig.show()

    def update_layout(self, fig: go.Figure) -> None:
        """Update the layout of the figure."""


__all__ = ["Plotter"]
