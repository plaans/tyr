import os
import platform
import sys
import time
from typing import List, Optional, TextIO

from tyr.cli.bench.collector import CollectionResult
from tyr.cli.writter import Writter
from tyr.planners.model.config import SolveConfig
from tyr.planners.model.planner import Planner
from tyr.planners.model.result import PlannerResult, PlannerResultStatus
from tyr.problems.model.domain import AbstractDomain
from tyr.problems.model.instance import ProblemInstance


class BenchTerminalWritter(Writter):
    """Utility class to write content of the benchmark on the terminal."""

    _status_map = {
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
        out: Optional[TextIO] = None,
        verbosity: int = 0,
    ) -> None:
        super().__init__(out, verbosity)
        self._solve_config = solve_config
        self._num_to_run = 0
        self._current_domain: Optional[AbstractDomain] = None
        self._current_version: str = ""
        self._main_color = "green"
        self._results: List[PlannerResult] = []
        self._starttime = 0

    # ================================== Session ================================= #

    def session_starts(self):
        """Prints information about the starting benchmark session."""
        self._starttime = time.time()

        self.separator("=", "Tyr bench session starts", bold=True)
        msg = f"platform {sys.platform} -- Python {platform.python_version()} -- {sys.executable}"
        self.line(msg)
        self.line(f"rootdir: {os.getcwd()}")
        self.report_solve_config()
        self.write("collecting...", flush=True, bold=True)

    def session_finished(self):
        """Prints summary of the finished benchmark session."""
        self.line()
        self.summary_errors()
        self.summary_short()
        self.summary_stats()

    # ================================== Summary ================================= #

    def summary_result_header(self, result: PlannerResult) -> str:
        """Formats the given the result to have an header to print on summary.

        Args:
            result (PlannerResult): The result to format.

        Returns:
            str: The formatted header.
        """
        return result.planner_name + " - " + result.problem.name

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
    ):
        """Prints a report about the collection of planners and problems.

        Args:
            planners (CollectionResult[Planner]): The collection result on planners.
            problems (CollectionResult[ProblemInstance]): The collection result on problems.
        """
        self._num_to_run = len(planners.selected) * len(problems.selected)

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

    def report_domain(self, domain: AbstractDomain):
        """Prints a report about a new running domain.

        Args:
            domain (AbstractDomain): The new domain.
        """
        self._current_domain = domain
        self.line()
        if not self.verbose:
            self.line(domain.name)

    def report_planner(self, planner: Planner):
        """Prints a report about a new running planner.

        Args:
            planner (Planner): The new planner.

        Raises:
            ValueError: When new current domain is registered.
        """
        if self._current_domain is None:
            raise ValueError("Unexpected null domain")
        self._current_version = planner.config.problems.get(
            self._current_domain.name, "none"
        )
        if not self.verbose:
            self.write(
                "    " + planner.name + ":" + self._current_version + " ", flush=True
            )

    def report_planner_finished(self):
        """Prints a report about a finishing planner."""
        if not self.verbose:
            self.report_progress()

    def report_planner_result(self, result: PlannerResult):
        """Prints a report about one resolution of a planner.

        Args:
            result (PlannerResult): The resolution result of the planner.
        """
        self._results.append(result)
        letter, markup_key = self._status_map[result.status]

        if markup_key == "red":
            self._main_color = "red"

        if not self.verbose:
            self.write(letter, **{markup_key: True})
            if self.current_line_width + len(" [100%]") > self._fullwidth:
                self.report_progress()
        else:
            planner, problem = result.planner_name, result.problem.name
            self.write(f"{planner} - {problem}:{self._current_version}")
            self.write(" " + result.status.name, **{markup_key: True})

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

    def report_progress(self):
        """Prints a report about the current progression status."""
        msg = f" [{int(len(self._results) / self._num_to_run * 100)}%]"
        fill = self._fullwidth - self.current_line_width
        self.line(msg.rjust(fill), **{self._main_color: True})

    def report_solve_config(self):
        """Prints a report about the configuration being used for the resolution."""
        msg = f"timeout: {self.format_seconds(self._solve_config.timeout)}"

        num_bytes = self._solve_config.memout
        msg += f" -- memout: {num_bytes} Bytes"
        for unit in ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
            if num_bytes < 1024:
                msg += f" ({num_bytes:.2f} {unit})"
                break
            num_bytes /= 1024
        self.line(msg)

    # ================================== Format ================================== #

    def format_seconds(self, seconds: int) -> str:
        """Formats the given number of seconds into a more readable format.

        Args:
            seconds (int): The seconds to format.

        Returns:
            str: The readable string.
        """
        msg = f"{seconds}s"
        if seconds >= 60:
            hours = seconds // 3600
            minutes = (seconds // 60) % 60
            seconds = seconds % 60
            if hours > 0:
                msg += f" ({hours:0>2}:{minutes:0>2}:{seconds:0>2})"
            else:
                msg += f" ({minutes:0>2}:{seconds:0>2})"
        return msg
