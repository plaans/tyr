import time
from pathlib import Path
from typing import List, Literal, Optional, TextIO, Tuple, Union

from tyr.cli.bench.collector import CollectionResult
from tyr.cli.writter import Writter
from tyr.planners.model.config import RunningMode, SolveConfig
from tyr.planners.model.planner import Planner
from tyr.planners.model.result import PlannerResult, PlannerResultStatus
from tyr.problems.model.instance import ProblemInstance


class SolveTerminalWritter(Writter):
    """Utility class to write content of the resolution on the terminal."""

    def __init__(
        self,
        solve_config: SolveConfig,
        out: Union[Optional[TextIO], List[TextIO]] = None,
        verbosity: int = 0,
        config: Optional[Path] = None,
    ) -> None:
        super().__init__(out, verbosity, config)
        self._solve_config = solve_config
        self._status = PlannerResultStatus.UNSUPPORTED

    # ================================== Report ================================== #

    def report_collect(
        self,
        planners: CollectionResult[Planner],
        problems: CollectionResult[ProblemInstance],
        running_mode: RunningMode,
    ) -> Union[Literal[False], Tuple[Planner, ProblemInstance]]:
        """Prints a report about the collection of planners and problems.

        Args:
            planners (CollectionResult[Planner]): The collection result on planners.
            problems (CollectionResult[ProblemInstance]): The collection result on problems.
            running_mode (RunningMode): The mode used to run planners resolution.

        Returns:
            Union[False, Tuple[Planner, ProblemInstance]]: False if an error occurred.
                The planner and the problem to use otherwise.
        """

        def report(result: CollectionResult, name: str) -> bool:
            if len(result.selected) == 0:
                self.line(f"No {name} found", bold=True)
                return False
            if len(result.selected) > 1:
                self.line(f"Multiple {name}s found", bold=True)
                for item in sorted(result.selected, key=lambda x: x.name):
                    self.line(f"\t{item.name}")
                return False
            return True

        self.rewrite("")

        if not report(planners, "planner"):
            return False
        if not report(problems, "problem"):
            return False

        planner, problem = planners.selected[0], problems.selected[0]
        self.line(f"{problem.name} with {planner.name} in {running_mode}", bold=True)
        return planner, problem

    def report_file(  # pylint: disable=too-many-arguments
        self,
        planner: Planner,
        result: PlannerResult,
        filename: str,
        title: str,
        color: str,
    ):
        """Prints a report about a file.

        Args:
            planner (Planner): The planner which did the resolution.
            result (PlannerResult): The result of the planner.
            filename (str): The filename to report.
            title (str): The title of the report.
            color (str): The color of the title.
        """

        file = planner.get_log_file(result.problem, filename, result.running_mode)
        if file.exists():
            self.line()
            self.separator("*", title, **{color: True})
            self.line()
            with open(file, "r", encoding="utf-8") as f:
                self.write(f.read())

    def report_result(self, planner: Planner, result: PlannerResult):
        """Prints a report about the resolution of the planner.

        Args:
            planner (Planner): The planner which did the resolution.
            result (PlannerResult): The result of the planner.
        """
        self._status = result.status
        self.report_file(planner, result, "solve", "Logs", "cyan")
        self.report_file(planner, result, "error", "Errors", "red")
        self.report_file(planner, result, "plan", "Plan", "green")
        self.line()

    # ================================== Session ================================= #

    def session_name(self) -> str:
        return "solve"

    def session_starts(self):
        super().session_starts()
        self.report_solve_config(self._solve_config)
        self.report_collecting()

    def session_finished(self):
        """Prints summary of the finished benchmark session."""
        self.line()
        self.summary_stats()

    # ================================== Summary ================================= #

    # pylint: disable=too-many-locals
    def summary_stats(self):
        """Prints a summary of the statistics of the run benchmark."""
        status_map = {
            PlannerResultStatus.SOLVED: "green",
            PlannerResultStatus.UNSOLVABLE: "red",
            PlannerResultStatus.TIMEOUT: "yellow",
            PlannerResultStatus.MEMOUT: "yellow",
            PlannerResultStatus.ERROR: "red",
            PlannerResultStatus.UNSUPPORTED: "blue",
        }

        session_duration = int(time.time() - self._starttime)
        msg = f"{self._status.name} in {self.format_seconds(session_duration)}"
        self.separator("=", msg, **{status_map[self._status]: True})


__all__ = ["SolveTerminalWritter"]
