from typing import List, Tuple

from tyr.planners.model.config import RunningMode
from tyr.planners.model.result import PlannerResult, PlannerResultStatus
from tyr.plotters.plotter import Plotter


# pylint: disable = use-dict-literal
class SurvivalPlotter(Plotter):
    """A plotter to visualize the performance of a planner using a survival plot."""

    def _title(self) -> str:
        """The title of the plot."""
        return "Survival Plot"

    def _xaxis(self) -> dict:
        """The x-axis properties."""
        return {"title": "Computation Time (seconds)", "type": "log"}

    def _yaxis(self) -> dict:
        """The y-axis properties."""
        return {"title": "# Instances"}

    def _data(self, data: List[PlannerResult]) -> Tuple[List[float], List[float]]:
        """Extract the data to plot."""
        # pylint: disable = duplicate-code

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


__all__ = ["SurvivalPlotter"]
