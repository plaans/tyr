import re
from typing import Dict, List, Tuple

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

    def _title(self) -> str:
        """The title of the plot."""
        return ""

    def _xaxis(self) -> Dict[str, str]:
        """The x-axis properties."""
        return {"title": ""}

    def _yaxis(self) -> Dict[str, str]:
        """The y-axis properties."""
        return {"title": ""}

    def _data(self, data: List[PlannerResult]) -> Tuple[List[float], List[float]]:
        """Extract the data to plot."""
        raise NotImplementedError

    def plot(self, results: List[PlannerResult]) -> None:
        """Plot the performance of a planner."""
        # pylint: disable = use-dict-literal

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
        fig.update_layout(
            title=self._title(),
            xaxis=self._xaxis(),
            yaxis=self._yaxis(),
        )

    # pylint: disable = too-many-locals
    def latex(self, results: List[PlannerResult]) -> str:
        """Return the LaTeX code of the plot."""

        planners = sorted(set(r.planner_name for r in results))
        domains = sorted(set(r.problem.domain.name for r in results))

        colors = [
            "red",
            "green",
            "blue",
            "cyan",
            "magenta",
            "yellow",
            "black",
            "gray",
            "white",
            "darkgray",
            "lightgray",
            "brown",
            "lime",
            "olive",
            "orange",
            "pink",
            "purple",
            "teal",
            "violet",
        ]
        symbols = [
            "*",
            "x ",
            "+",
            "|",
            "o",
            "asterisk",
            "star",
            "10-pointed star",
            "oplus",
            "oplus*",
            "otimes",
            "otimes*",
            "square",
            "square*",
            "triangle",
            "triangle*",
            "diamond",
            "halfdiamond*",
            "halfsquare*",
            "right*",
            "left*",
            "Mercedes star",
            "Mercedes star flipped",
            "halfcircle",
            "halfcircle*",
            "pentagon",
            "pentagon*",
        ]

        result = "\\begin{tikzpicture}\n\\begin{axis}[\n"
        result += f"title={{{self._title()}}},\n"
        result += f"xlabel={{{self._xaxis()['title']}}},\n"
        result += f"ylabel={{{self._yaxis()['title']}}},\n"
        result += "xmajorgrids=true,\n"
        result += "ymajorgrids=true,\n"
        result += "grid style=dashed,\n"
        result += "]\n"

        for i, planner in enumerate(planners):
            color = colors[i % len(colors)]
            for j, domain in enumerate(domains):
                symbol = symbols[j % len(symbols)]
                data = self._data(
                    [
                        r
                        for r in results
                        if r.planner_name == planner and r.problem.domain.name == domain
                    ]
                )

                result += "\\addplot[\n"
                result += f"color={color},\n"
                result += f"mark={symbol},\n"
                result += "mark size=2,\n"
                result += f"mark options={{fill={color}}},\n"
                result += "smooth,\n"
                result += "]\n"
                result += "coordinates {\n"
                for x, y in zip(data[0], data[1]):
                    result += f"({x}, {y})\n"
                result += "};\n"
                result += f"\\addlegendentry{{{planner} - {domain}}}\n"

        result += "\\end{axis}\n\\end{tikzpicture}\n"
        return result


__all__ = ["Plotter"]
