from fractions import Fraction
from pathlib import Path
from typing import Any, List, Optional

from unified_planning.engines.results import (
    LogMessage,
    PlanGenerationResultStatus,
    PlanGenerationResult,
)
from unified_planning.io import PDDLWriter
from unified_planning.shortcuts import Problem

from tyr.planners.model.pddl_planner import TyrPDDLPlanner


class PopfPlanner(TyrPDDLPlanner):
    """
    The POPF planner wrapped into local PDDL planner.

    NOTE: In Anytime mode, the planner will only return the last plan found.
    """

    def _get_cmd(
        self,
        domain_filename: str,
        problem_filename: str,
        plan_filename: str,
    ) -> List[str]:
        return (
            " ".join(
                self._get_anytime_cmd(
                    domain_filename,
                    problem_filename,
                    plan_filename,
                )
            )
            .replace("-n", "")
            .split()
        )

    def _get_anytime_cmd(
        self,
        domain_filename: str,
        problem_filename: str,
        plan_filename: str,
    ) -> List[str]:
        binary = (Path(__file__).parent / "popf").resolve().as_posix()
        return f"{binary} -n {domain_filename} {problem_filename}".split()

    def _parse_planner_output(self, writer, planner_output):
        assert isinstance(self._writer, PDDLWriter)
        for l in planner_output.splitlines():
            if self._starting_plan_str() in l:
                writer.storing = True
            elif writer.storing and "" == l:
                plan_str = "\n".join(writer.current_plan)
                plan = self._plan_from_str(
                    writer.problem, plan_str, self._writer.get_item_named
                )
                res = PlanGenerationResult(
                    PlanGenerationResultStatus.INTERMEDIATE,
                    plan=plan,
                    engine_name=self.name,
                )
                writer.res_queue.put(res)
                writer.current_plan = []
                writer.storing = False
            elif writer.storing and l:
                writer.current_plan.append(self._parse_plan_line(l))

    def _get_engine_epsilon(self) -> Optional[Fraction]:
        return Fraction(1, 1000)

    def _get_computation_time(self, logs: List[LogMessage]) -> Optional[float]:
        for log in logs:
            for line in reversed(log.message.splitlines()):
                if line.startswith("; Time"):
                    return float(line.split()[2])
        return None

    def _get_plan(self, proc_out: List[str]) -> str:
        plan: List[str] = []
        parsing = False
        for line in proc_out:
            if self._starting_plan_str() in line:
                parsing = True
                plan = []  # Clear the plan to keep only the last one
                continue
            if not parsing:
                continue
            if self._ending_plan_str() == line:
                parsing = False
            plan.append(self._parse_plan_line(line))
        return "\n".join(plan)

    def _starting_plan_str(self) -> str:
        return "; Time"

    def _ending_plan_str(self) -> str:
        return "\n"

    def _parse_plan_line(self, plan_line: str) -> str:
        return plan_line

    def _result_status(
        self,
        problem: Problem,
        plan: Optional[Any],
        retval: int,
        log_messages: Optional[List[LogMessage]] = None,
    ) -> PlanGenerationResultStatus:
        if plan is not None:
            splitted = str(plan).strip().split("\n")
            has_plan = len(splitted) > 1
        else:
            has_plan = False

        if has_plan:
            return PlanGenerationResultStatus.SOLVED_SATISFICING
        print(retval)
        if retval == 0:
            return PlanGenerationResultStatus.UNSOLVABLE_INCOMPLETELY
        return PlanGenerationResultStatus.INTERNAL_ERROR


__all__ = ["PopfPlanner"]
