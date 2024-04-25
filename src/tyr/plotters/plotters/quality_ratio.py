from collections import namedtuple
from typing import List, Tuple

import plotly.graph_objects as go

from tyr.planners.model.config import RunningMode
from tyr.planners.model.result import PlannerResult
from tyr.plotters.plotter import Plotter


class QualityRatioPlotter(Plotter):
    """
    A plotter to compare the performances of two planners using
    a Quality Ratio plot.
    """

    def __init__(self) -> None:
        super().__init__()
        self._planner_names: List[str] = []

    def _title(self) -> str:
        return "Quality Ratio Plot"

    def _xaxis(self) -> dict:
        return {"title": "Instances"}

    def _yaxis(self) -> dict:
        return {"title": "Improvement Ratio"}

    def _data(self, data: List[PlannerResult]) -> Tuple[List[float], List[float]]:
        """Extract the data to plot."""
        # Extract the planner names
        self._planner_names = sorted(list({r.planner_name for r in data}))
        if len(self._planner_names) != 2:
            raise ValueError("Quality Ratio plot requires exactly two planners.")

        # Sort results by planner name
        planner_results = [
            sorted(
                PlannerResult.merge_all([r for r in data if r.planner_name == name]),
                key=lambda r: r.problem.name,
            )
            for name in self._planner_names
        ]

        # Compute the solved values
        Point = namedtuple("Point", ["timeout", "value"])
        raw_data = []
        for res1, res2 in zip(planner_results[0], planner_results[1]):
            if res1.problem.name != res2.problem.name:
                raise ValueError("Quality Ratio plot needs the same instances.")
            if res1.running_mode not in (RunningMode.ANYTIME, RunningMode.MERGED):
                continue
            if res2.running_mode not in (RunningMode.ANYTIME, RunningMode.MERGED):
                continue
            q1, q2 = res1.plan_quality, res2.plan_quality

            # Plot only if at least one has solved the instance
            if q1 is None and q2 is None:
                continue

            # Only one planner has solved the instance
            if q1 is None or q2 is None:
                raw_data.append(Point(timeout=q1 is None, value=None))
            else:
                q1 += 1  # Avoid division by zero
                q2 += 1  # Avoid division by zero
                value = 0 if q1 == q2 else -q1 / q2 + 1 if q1 > q2 else q2 / q1 - 1
                raw_data.append(Point(timeout=None, value=value))

        # Compute the unsolved values
        min_value = min((p.value for p in raw_data if p.value is not None), default=-1)
        max_value = max((p.value for p in raw_data if p.value is not None), default=1)
        extremum = 1.2 * max(abs(min_value), abs(max_value))
        final_data = []
        for d in raw_data:
            if d.value is not None:
                final_data.append(d)
                continue
            if d.timeout is None:
                raise ValueError("Timeout should not be null when value is null.")
            value = -extremum if d.timeout else extremum
            final_data.append(d._replace(value=value))

        # Sort data by value
        final_data.sort(key=lambda d: d.value)
        return list(range(len(final_data))), [d.value for d in final_data]

    # pylint: disable = use-dict-literal, duplicate-code
    def plot(self, results: List[PlannerResult]) -> None:
        """Plot the performance of a planner."""
        # Extract the data
        x, y = self._data(results)
        extremum = max(abs(min(y)), abs(max(y)))

        # Plot the data
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                line=dict(width=2),
                marker=dict(size=8),
                fill="tozeroy",
                showlegend=False,
            )
        )

        # Plot guidelines
        fig.add_hline(
            y=0, line=dict(width=5, color="darkgray"), annotation_text="Equality"
        )
        fig.add_hline(
            y=extremum,
            line=dict(width=5, color="lightcoral"),
            annotation_text=f"Unsolved by {self._planner_names[1]}",
        )
        fig.add_hline(
            y=-extremum,
            line=dict(width=5, color="lightcoral"),
            annotation_text=f"Unsolved by {self._planner_names[0]}",
            annotation_position="bottom right",
        )

        # Plot planner names
        fig.add_trace(
            go.Scatter(
                x=[1, 1],
                y=[1, -1],
                mode="text",
                text=[f"{n} is better" for n in self._planner_names],
                textposition=["top right", "bottom right"],
                showlegend=False,
            )
        )

        # Update the layout & show the plot
        self.update_layout(fig)
        fig.show()

    def latex(self, results: List[PlannerResult]) -> str:

        data = self._data(results)
        max_x = max(data[0])
        min_y, max_y = min(data[1]), max(data[1])

        result = "\\begin{tikzpicture}\n\\begin{axis}[\n"
        result += f"title={{{self._title()}}},\n"
        result += f"xlabel={{{self._xaxis()['title']}}},\n"
        result += f"ylabel={{{self._yaxis()['title']}}},\n"
        result += f"xmin=0,xmax={max_x},\n"
        result += "xmajorgrids=true,\n"
        result += "ymajorgrids=true,\n"
        result += "grid style=dashed,\n"
        result += "]\n"

        result += "\\addplot[\n"
        result += "color=blue,\n"
        result += "fill=blue!20,\n"
        result += "mark=+,\n"
        result += "mark size=2,\n"
        result += "]\n"
        result += "coordinates {\n"
        for x, y in zip(data[0], data[1]):
            result += f"({x}, {y})\n"
        result += "} \\closedcycle;\n"

        result += f"\\draw (axis cs:0,0) -- (axis cs:{max_x},0);\n"
        result += f"\\node [below left] at (axis cs:{max_x},0) {{Equality}};\n"
        result += f"\\draw [red] (axis cs:0,{min_y}) -- (axis cs:{max_x},{min_y});\n"
        result += (
            f"\\node [below left] at (axis cs:{max_x},{min_y}) "
            f"{{Unsolved by {self._planner_names[0]}}};\n"
        )
        result += f"\\draw [red] (axis cs:0,{max_y}) -- (axis cs:{max_x},{max_y});\n"
        result += (
            f"\\node [above left] at (axis cs:{max_x},{max_y}) "
            f"{{Unsolved by {self._planner_names[1]}}};\n"
        )
        result += f"\\node [above right] at (axis cs:0,0) {{{self._planner_names[0]} is better}};\n"
        result += f"\\node [below right] at (axis cs:0,0) {{{self._planner_names[1]} is better}};\n"

        result += "\\end{axis}\n\\end{tikzpicture}\n"
        return result


__all__ = ["QualityRatioPlotter"]
