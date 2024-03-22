from typing import List

import plotly.graph_objects as go
from plotly.colors import DEFAULT_PLOTLY_COLORS
from plotly.validators.scatter.marker import SymbolValidator

from tyr.planners.model.result import PlannerResult, PlannerResultStatus


# pylint: disable = use-dict-literal
def cactus_plot(results: List[PlannerResult]):
    planners = sorted(set(r.planner_name for r in results))
    domains = sorted(set(r.problem.domain.name for r in results))
    symbols = SymbolValidator().values
    fig = go.Figure()

    for i, planner in enumerate(planners):
        color = DEFAULT_PLOTLY_COLORS[i % len(DEFAULT_PLOTLY_COLORS)]
        for j, domain in enumerate(domains):
            symbol = symbols[(j * 12) % len(symbols) + 2]
            times = sorted(
                [
                    float(r.computation_time or r.config.timeout)
                    for r in results
                    if r.planner_name == planner
                    and r.problem.domain.name == domain
                    and r.status == PlannerResultStatus.SOLVED
                ]
            )
            fig.add_trace(
                go.Scatter(
                    x=list(range(1, len(times) + 1)),
                    y=[sum(times[: i + 1]) for i in range(len(times))],
                    mode="lines+markers",
                    line=dict(color=color, width=2),
                    marker=dict(color=color, size=8, symbol=symbol),
                    name=f"{planner} - {domain}",
                )
            )

    fig.update_layout(
        title="Cactus Plot",
        xaxis=dict(
            title="# Instances",
        ),
        yaxis=dict(
            title="Computation Time (seconds)",
            type="log",
        ),
    )
    fig.show()


__all__ = ["cactus_plot"]
