import os
import re
import time
from typing import IO, Callable, Dict, List, Optional, Tuple, Union

from unified_planning.engines import pddl_planner as upf_pddl_planner
from unified_planning.engines.pddl_anytime_planner import PDDLAnytimePlanner, Writer
from unified_planning.engines.results import (
    LogLevel,
    LogMessage,
    PlanGenerationResult,
    PlanGenerationResultStatus,
    correct_plan_generation_result,
)
from unified_planning.plans import TimeTriggeredPlan
from unified_planning.shortcuts import AbstractProblem, ProblemKind, State

from tyr.planners.model.pddl_writer import TyrPDDLWriter


class TyrPDDLPlanner(PDDLAnytimePlanner):
    """A local wrapper from unified planning PDDL Planner."""

    _writer: Optional[TyrPDDLWriter]

    @property
    def name(self):
        base_name = self.__class__.__name__[:-7]
        return re.sub(r"([A-Z])", r"-\1", base_name).lower().lstrip("-")

    @staticmethod
    def supported_kind() -> ProblemKind:
        raise NotImplementedError()

    @staticmethod
    def supports(_) -> bool:
        return True

    def _file_extension(self) -> str:
        return "pddl"

    def _get_computation_time(self, _logs: List[LogMessage]) -> Optional[float]:
        return None

    def _get_plan(self, proc_out: List[str]) -> str:
        return "\n".join(proc_out)

    def _get_write_domain_options(self) -> Dict[str, bool]:
        return {}

    # pylint: disable=too-many-arguments, too-many-positional-arguments, too-many-locals
    # pylint: disable=too-many-branches, too-many-statements
    def _solve(  # pragma: no cover # Copy of the original method with really small changes
        self,
        problem: AbstractProblem,
        heuristic: Optional[Callable[[State], Optional[float]]] = None,
        timeout: Optional[float] = None,
        output_stream: Optional[Union[Tuple[IO[str], IO[str]], IO[str]]] = None,
        anytime: bool = False,
    ) -> PlanGenerationResult:
        try:
            self._writer = TyrPDDLWriter(
                problem,
                self._needs_requirements,
                self._rewrite_bool_assignments,
            )
            plan = None
            logs: List[LogMessage] = []

            if output_stream is None:
                raise RuntimeError("Output stream is required for Tyr PDDL planners.")
            if isinstance(output_stream, tuple):
                output_stream = output_stream[0]
            base_stream = (
                output_stream._output_stream  # pylint: disable=protected-access
                if isinstance(output_stream, Writer)
                else output_stream
            )
            output_dir = os.sep.join(base_stream.name.split(os.sep)[:-1])

            ext = self._file_extension()
            domain_filename = os.path.join(output_dir, f"domain.{ext}")
            problem_filename = os.path.join(output_dir, f"problem.{ext}")
            plan_filename = os.path.join(output_dir, "output.plan")
            domain_options = self._get_write_domain_options()
            self._writer.write_domain(domain_filename, **domain_options)
            self._writer.write_problem(problem_filename)
            if anytime:
                cmd = self._get_anytime_cmd(
                    domain_filename,
                    problem_filename,
                    plan_filename,
                )
            else:
                cmd = self._get_cmd(
                    domain_filename,
                    problem_filename,
                    plan_filename,
                )
            process_start = time.time()

            exec_res = upf_pddl_planner.run_command_posix_select(
                cmd, output_stream, timeout
            )
            timeout_occurred, (proc_out, proc_err), retval = exec_res

            process_end = time.time()
            logs.append(LogMessage(LogLevel.INFO, "".join(proc_out)))
            logs.append(LogMessage(LogLevel.ERROR, "".join(proc_err)))
            if os.path.isfile(plan_filename):
                plan = self._plan_from_file(
                    problem,
                    plan_filename,
                    self._writer.get_item_named,
                )
            elif os.path.isfile(plan_filename + ".1"):
                i = 2
                if anytime:
                    while os.path.isfile(plan_filename + f".{i}"):
                        i += 1
                plan = self._plan_from_file(
                    problem,
                    plan_filename + f".{i - 1}",
                    self._writer.get_item_named,
                )
            else:
                plan = self._plan_from_str(
                    problem,
                    self._get_plan(proc_out),
                    self._writer.get_item_named,
                )
            has_plan = plan is not None and len(str(plan).splitlines()) > 1

            metrics: Dict[str, str] = {}
            # pylint: disable=assignment-from-none
            computation = self._get_computation_time(logs)
            if computation is None:
                # If computation time is not provided, use the process time
                computation = process_end - process_start
            metrics["engine_internal_time"] = str(computation)

            # Improved timeout detection:
            # 1. Check if run_command reported a timeout
            # 2. Check if computation time exceeds timeout
            if timeout_occurred:
                # run_command already detected a timeout
                pass
            elif timeout is not None:
                # Check if computation time suggests timeout
                timeout_occurred = computation >= timeout - 1

            if timeout_occurred and not has_plan:
                return PlanGenerationResult(
                    PlanGenerationResultStatus.TIMEOUT,
                    plan=plan,
                    engine_name=self.name,
                    log_messages=logs,
                    metrics=metrics,
                )

            status = self._result_status(problem, plan, retval, logs)
            res = PlanGenerationResult(
                status,
                plan,
                engine_name=self.name,
                log_messages=logs,
                metrics=metrics,
            )
            problem_kind = problem.kind
            if problem_kind.has_continuous_time() or problem_kind.has_discrete_time():
                if isinstance(plan, TimeTriggeredPlan) or plan is None:
                    return correct_plan_generation_result(
                        res, problem, self._get_engine_epsilon()
                    )
            return res
        except Exception as e:  # pylint: disable=broad-exception-caught
            return PlanGenerationResult(
                PlanGenerationResultStatus.INTERNAL_ERROR,
                plan=None,
                engine_name=self.name,
                log_messages=[LogMessage(LogLevel.ERROR, str(e))],
            )

    def check_for_plan_from_files(
        self,
        problem: AbstractProblem,
        output_dir: str,
        anytime: bool,
    ) -> Optional[PlanGenerationResult]:
        """
        Check for plan files after process termination and parse if found.

        Args:
            problem: The problem being solved
            output_dir: Directory where plan files are written
            anytime: Whether the planner is in anytime mode

        Returns:
            PlanGenerationResult if a plan file is found and parsed successfully, None otherwise
        """

        self._writer = TyrPDDLWriter(
            problem,
            self._needs_requirements,
            self._rewrite_bool_assignments,
        )

        plan = None
        ext = self._file_extension()
        domain_filename = os.path.join(output_dir, f"domain.{ext}")
        problem_filename = os.path.join(output_dir, f"problem.{ext}")
        plan_filename = os.path.join(output_dir, "output.plan")
        domain_options = self._get_write_domain_options()
        self._writer.write_domain(domain_filename, **domain_options)
        self._writer.write_problem(problem_filename)

        # Check for output.plan first
        if os.path.isfile(plan_filename):
            plan = self._plan_from_file(
                problem,
                plan_filename,
                self._writer.get_item_named,
            )
        # Check for output.plan.1, output.plan.2, etc.
        elif os.path.isfile(plan_filename + ".1"):
            i = 2
            # For anytime mode, find the latest plan file
            if anytime:
                while os.path.isfile(plan_filename + f".{i}"):
                    i += 1
            plan = self._plan_from_file(
                problem,
                plan_filename + f".{i - 1}",
                self._writer.get_item_named,
            )
        has_plan = plan is not None and len(str(plan).splitlines()) > 1

        metrics: Dict[str, str] = {}
        # pylint: disable=assignment-from-none
        computation = self._get_computation_time([])
        if computation is not None:
            metrics["engine_internal_time"] = str(computation)

        self._writer = None
        if has_plan:
            return PlanGenerationResult(
                PlanGenerationResultStatus.SOLVED_SATISFICING,
                plan=plan,
                engine_name=self.name,
                log_messages=[
                    LogMessage(LogLevel.INFO, "Plan recovered after timeout")
                ],
                metrics=metrics,
            )
        return None


__all__ = ["TyrPDDLPlanner"]
