from typing import List
from tyr.cli.collector import CollectionResult
from tyr.cli.writter import Writter
from tyr.planners.model.planner import Planner
from tyr.planners.model.result import PlannerResult
from tyr.plotters.plotter import Plotter
from tyr.problems.model.instance import ProblemInstance


class PlotTerminalWritter(Writter):
    """A terminal writter for the plot command."""

    def report_collect(
        self,
        planners: CollectionResult[Planner],
        problems: CollectionResult[ProblemInstance],
        plotters: CollectionResult[Plotter],
    ) -> None:
        """Prints a report about the collection of planners, problems and plotters.

        Args:
            planners (CollectionResult[Planner]): The collection result on planners.
            problems (CollectionResult[ProblemInstance]): The collection result on problems.
            plotters (CollectionResult[Plotter]): The collection result on plotters.
        """
        self.rewrite("")
        self.report_collected(planners, "planner")
        self.report_collected(problems, "problem")
        self.report_collected(plotters, "plotter")

    def report_results(self, results: List[PlannerResult]):
        """Prints a report about the collected results."""
        total = len(results)
        msg = f"collected {total} result" + ("" if total <= 1 else "s")
        self.line(msg, bold=True)

    def session_name(self) -> str:
        return "plot"


__all__ = ["PlotTerminalWritter"]
