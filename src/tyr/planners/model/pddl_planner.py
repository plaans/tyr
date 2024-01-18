import os
import re
import subprocess  # nosec: B404
import tempfile
import time
from typing import IO, Callable, List, Optional, Tuple, Union

from unified_planning.engines.pddl_planner import PDDLPlanner, run_command_posix_select
from unified_planning.engines.results import (
    LogLevel,
    LogMessage,
    PlanGenerationResult,
    PlanGenerationResultStatus,
    correct_plan_generation_result,
)
from unified_planning.environment import get_environment
from unified_planning.io import PDDLWriter
from unified_planning.plans import TimeTriggeredPlan
from unified_planning.shortcuts import AbstractProblem, ProblemKind, State


class TyrPDDLPlanner(PDDLPlanner):
    """A local wrapper from unified planning PDDL Planner."""

    @classmethod
    def _get_name(cls) -> str:
        return re.sub(r"([A-Z])", r"-\1", cls.__name__[:-7]).lower().lstrip("-")

    @classmethod
    def register(cls):
        """Registers the planner into unified planning."""
        env = get_environment()
        env.factory.add_engine(cls._get_name(), cls.__module__, cls.__name__)

    @property
    def name(self):
        return self._get_name()

    @staticmethod
    def supported_kind() -> ProblemKind:
        raise NotImplementedError()

    @staticmethod
    def supports(_) -> bool:
        return True

    def _get_plan(self, proc_out: List[str]) -> str:
        raise NotImplementedError()

    # pylint: disable=too-many-locals
    def _solve(
        self,
        problem: AbstractProblem,
        heuristic: Optional[Callable[[State], Optional[float]]] = None,
        timeout: Optional[float] = None,
        output_stream: Optional[Union[Tuple[IO[str], IO[str]], IO[str]]] = None,
    ) -> PlanGenerationResult:
        self._writer = PDDLWriter(
            problem,
            self._needs_requirements,
            self._rewrite_bool_assignments,
        )
        plan = None
        logs: List[LogMessage] = []

        with tempfile.TemporaryDirectory() as tempdir:
            domain_filename = os.path.join(tempdir, "domain.pddl")
            problem_filename = os.path.join(tempdir, "problem.pddl")
            plan_filename = os.path.join(tempdir, "plan.txt")
            self._writer.write_domain(domain_filename)
            self._writer.write_problem(problem_filename)
            cmd = self._get_cmd(domain_filename, problem_filename, plan_filename)
            process_start = time.time()

            if output_stream is None:
                # If we do not have an output stream to write to, we simply call
                # a subprocess and retrieve the final output and error with communicate
                with subprocess.Popen(  # nosec: B603
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                ) as process:
                    timeout_occurred: bool = False
                    proc_out: List[str] = []
                    proc_err: List[str] = []
                    try:
                        out_err_bytes = process.communicate(timeout=timeout)
                        proc_out, proc_err = [[x.decode()] for x in out_err_bytes]
                    except subprocess.TimeoutExpired as err:
                        proc_out = err.output.decode() if err.output is not None else []
                        timeout_occurred = True
                    retval = process.returncode
            else:
                exec_res = run_command_posix_select(self, cmd, output_stream, timeout)
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
            else:
                plan = self._plan_from_str(
                    problem,
                    self._get_plan(proc_out),
                    self._writer.get_item_named,
                )

            metrics = {}
            metrics["engine_internal_time"] = str(process_end - process_start)
            if timeout_occurred and retval != 0:
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
