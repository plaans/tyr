import time
from dataclasses import dataclass
from typing import Dict, List, Optional, TextIO, Tuple, Union

from tyr.cli.bench.collector import CollectionResult
from tyr.cli.writter import Writter
from tyr.planners.model.config import RunningMode, SolveConfig
from tyr.planners.model.planner import Planner
from tyr.planners.model.result import PlannerResult, PlannerResultStatus
from tyr.problems.model.domain import AbstractDomain
from tyr.problems.model.instance import ProblemInstance


@dataclass
class BenchResult:
    """The minimal representation of a result for the writter."""

    status: PlannerResultStatus
    planner_name: str
    running_mode: RunningMode
    problem_name: str
    error_message: str

    @staticmethod
    def from_planner(result: PlannerResult) -> "BenchResult":
        """Converts the given planner result into bench result.

        Args:
            result (PlannerResult): The result to convert.

        Returns:
            BenchResult: The converted result.
        """
        return BenchResult(
            result.status,
            result.planner_name,
            result.running_mode,
            result.problem.name,
            result.error_message,
        )


class BenchTerminalWritter(Writter):
    """Utility class to write content of the benchmark on the terminal."""

    _status_map: Dict[PlannerResultStatus, Tuple[str, str]] = {
        PlannerResultStatus.SOLVED: (".", "green"),
        PlannerResultStatus.UNSOLVABLE: ("U", "red"),
        PlannerResultStatus.TIMEOUT: ("T", "yellow"),
        PlannerResultStatus.MEMOUT: ("M", "yellow"),
        PlannerResultStatus.ERROR: ("E", "red"),
        PlannerResultStatus.UNSUPPORTED: (".", "blue"),
    }

    def __init__(
        self,
        solve_config: SolveConfig,
        out: Union[Optional[TextIO], List[TextIO]] = None,
        verbosity: int = 0,
    ) -> None:
        super().__init__(out, verbosity)
        self._solve_config = solve_config
        self._num_to_run = 0
        self._main_color = "green"
        self._results: List[BenchResult] = []
        self._starttime = 0

    # =============================== Manipulation =============================== #

    def set_results(self, results: List[BenchResult]):
        """Modifies the stored results.

        Args:
            results (List[BenchResult]): The new results to store.
        """
        self._results = results

    # ================================== Session ================================= #

    def session_name(self) -> str:
        return "bench"

    def session_starts(self):
        super().session_starts()
        self.report_solve_config(self._solve_config)
        self.line(
            f"parallel: {self._solve_config.jobs} job"
            + ("" if self._solve_config.jobs == 1 else "s")
        )
        self.report_collecting()

    def session_finished(self):
        """Prints summary of the finished benchmark session."""
        self.line()
        self.summary_errors()
        self.summary_short()
        self.summary_stats()

    # ================================== Summary ================================= #

    def summary_result_header(self, result: BenchResult) -> str:
        """Formats the given the result to have an header to print on summary.

        Args:
            result (PlannerResult): The result to format.

        Returns:
            str: The formatted header.
        """
        return (
            result.planner_name
            + " - "
            + result.running_mode.name.lower()
            + " - "
            + result.problem_name
        )

    def summary_errors(self):
        """Prints a summary about the errors that occurred."""
        error_results = [
            result
            for result in self._results
            if result.status == PlannerResultStatus.ERROR
        ]
        if len(error_results) == 0:
            return

        self.separator("=", "ERRORS")
        for result in error_results:
            self.separator("_", self.summary_result_header(result), red=True)
            if len(result.error_message.strip()) != 0:
                self.line("\n" + result.error_message)

    def summary_short(self):
        """Prints a short summary about the errors and the unsolved problems."""
        results = [
            result
            for result in self._results
            if result.status
            in [PlannerResultStatus.ERROR, PlannerResultStatus.UNSOLVABLE]
        ]
        if len(results) == 0:
            return

        fullwidth = self._fullwidth
        max_header_length = max(len(self.summary_result_header(r)) for r in results)
        max_tpe = (
            "UNSOLVABLE"
            if any(r.status == PlannerResultStatus.UNSOLVABLE for r in results)
            else "ERROR"
        )
        column_width = max_header_length + len(f"  {max_tpe} ")
        num_columns = fullwidth // column_width

        self.separator("=", "short summary", cyan=True, bold=True)
        for i, result in enumerate(results):
            if (i % num_columns) != 0:
                self.write("  ")
            msgl = len(result.status.name) + len(self.summary_result_header(result)) + 1
            fill = " " * (column_width - msgl)
            tpe = self.markup(result.status.name, red=True)
            self.write(f"{tpe} {self.summary_result_header(result)}{fill}")
            if (i % num_columns) == (num_columns - 1):
                self.line()
        if self.current_line_width != 0:
            self.line()

    # pylint: disable=too-many-locals
    def summary_stats(self):
        """Prints a summary of the statistics of the run benchmark."""
        session_duration = int(time.time() - self._starttime)
        preferred_parts_order = [
            PlannerResultStatus.ERROR,
            PlannerResultStatus.UNSOLVABLE,
            PlannerResultStatus.SOLVED,
            PlannerResultStatus.UNSUPPORTED,
            PlannerResultStatus.TIMEOUT,
            PlannerResultStatus.MEMOUT,
        ]

        parts = []
        for status in preferred_parts_order:
            number = len([r for r in self._results if r.status == status])
            if number == 0:
                continue

            _, color = self._status_map[status]
            msg = f"{number} {status.name.lower()}"
            markup = {color: True}
            parts.append((msg, markup))

        line_parts = []
        fullwidth = self._fullwidth
        for text, markup in parts:
            with_markup = self.markup(text, **markup)
            fullwidth += len(with_markup) - len(text)
            line_parts.append(with_markup)
        msg = ", ".join(line_parts)

        main_markup = {self._main_color: True}
        duration = f" in {self.format_seconds(session_duration)}"
        duration_with_markup = self.markup(duration, **main_markup)
        fullwidth += len(duration_with_markup) - len(duration)
        msg += duration_with_markup

        markup_for_end_sep = self.markup("", **main_markup)
        if markup_for_end_sep.endswith("\x1b[0m"):
            markup_for_end_sep = markup_for_end_sep[:-4]
        fullwidth += len(markup_for_end_sep)
        msg += markup_for_end_sep

        self.separator("=", msg, fullwidth=fullwidth, **main_markup)

    # ================================== Report ================================== #

    def report_collect(
        self,
        planners: CollectionResult[Planner],
        problems: CollectionResult[ProblemInstance],
        running_modes: List[RunningMode],
    ):
        """Prints a report about the collection of planners and problems.

        Args:
            planners (CollectionResult[Planner]): The collection result on planners.
            problems (CollectionResult[ProblemInstance]): The collection result on problems.
            running_modes (List[RunningMode]): The mode used to run planners resolutions.
        """
        self._num_to_run = (
            len(planners.selected) * len(problems.selected) * len(running_modes)
        )

        def report(result: CollectionResult, name: str):
            total = result.total
            selected = len(result.selected)
            deselected = len(result.deselected)
            skipped = len(result.skipped)

            line = f"collected {total} {name}" + ("" if total <= 1 else "s")
            if deselected:
                line += f" / {deselected} deselected"
            if skipped:
                line += f" / {skipped} skipped"
            if total > selected:
                line += f" / {selected} selected"

            self.line(line, bold=True)

        self.rewrite("")
        report(planners, "planner")
        report(problems, "problem")

    def report_running_mode(self, running_mode: RunningMode):
        """Prints a report about a new running mode.

        Args:
            running_mode (RunningMode): The new running mode.
        """
        self.line()
        self.separator("*", running_mode.name.title())

    def report_domain(self, domain: AbstractDomain):
        """Prints a report about a new running domain.

        Args:
            domain (AbstractDomain): The new domain.
        """
        if self._solve_config.jobs == 1:
            self.line()
            if not self.verbose:
                self.line(domain.name)

    def report_planner(self, domain: AbstractDomain, planner: Planner):
        """Prints a report about a new running planner.

        Args:
            domain (AbstractDomain): The domain the planner will solve.
            planner (Planner): The new planner.

        Raises:
            ValueError: When new current domain is registered.
        """
        current_version = planner.config.problems.get(domain.name, "none")
        if not self.verbose and self._solve_config.jobs == 1:
            self.write("    " + planner.name + ":" + current_version + " ", flush=True)

    def report_planner_finished(self):
        """Prints a report about a finishing planner."""
        if not self.verbose and self._solve_config.jobs == 1:
            self.report_progress()

    def report_planner_result(
        self,
        domain: AbstractDomain,
        planner: Planner,
        result: PlannerResult,
    ):
        """Prints a report about one resolution of a planner.

        Args:
            domain (AbstractDomain): The solve domain.
            planner (Planner): The planner performing the resolution.
            result (PlannerResult): The resolution result of the planner.
        """
        self._results.append(BenchResult.from_planner(result))
        letter, markup_key = self._status_map[result.status]

        markup = {markup_key: True}
        if result.from_database:
            markup["invert"] = True

        if markup_key == "red":
            self._main_color = "red"

        if not self.verbose:
            self.write(letter, **markup)
            if self.current_line_width + len(" [100%]") > self._fullwidth:
                self.report_progress()
        else:
            current_version = planner.config.problems.get(domain.name, "none")
            if self._solve_config.jobs == 1:
                self.rewrite(
                    f"{planner.name} - {result.problem.name}:{current_version}"
                )
            else:
                self.write(
                    f"{planner.name} - {result.running_mode.name.lower()} - \
{result.problem.name}:{current_version}"
                )
            self.write(" ")
            self.write(result.status.name, **markup)

            if (comp_time := result.computation_time) is not None and (
                result.status
                not in [PlannerResultStatus.TIMEOUT, PlannerResultStatus.UNSUPPORTED]
            ):
                self.write(" " + self.format_seconds(int(comp_time)), purple=True)

            if (
                result.status is PlannerResultStatus.SOLVED
                and result.plan_quality is not None
            ):
                self.write(f" {result.plan_quality}", cyan=True)

            self.report_progress()

        self.flush()

    def report_planner_started(
        self,
        domain: AbstractDomain,
        planner: Planner,
        problem: ProblemInstance,
    ):
        """Prints a report about a starting planner.

        Args:
            domain (AbstractDomain): The domain the planner will solve.
            planner (Planner): The planner starting the resolution.
            problem (ProblemInstance): The problem to solve.
        """
        if self.verbose and self._solve_config.jobs == 1:
            current_version = planner.config.problems.get(domain.name, "none")
            current_date = self.markup(time.strftime("%Y-%m-%d %H:%M:%S"), purple=True)
            self.write(
                f"{planner.name} - {problem.name}:{current_version} started at {current_date}",
                flush=True,
            )

    def report_progress(self):
        """Prints a report about the current progression status."""
        msg = f" [{int(len(self._results) / self._num_to_run * 100)}%]"
        fill = self._fullwidth - self.current_line_width
        self.line(msg.rjust(fill), **{self._main_color: True})


__all__ = ["BenchResult", "BenchTerminalWritter"]
