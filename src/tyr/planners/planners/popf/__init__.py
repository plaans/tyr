import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, List, Optional

from unified_planning.engines.results import LogMessage, PlanGenerationResultStatus
from unified_planning.plans import Plan
from unified_planning.shortcuts import AbstractProblem, Problem

from tyr.planners.model.pddl_planner import TyrPDDLPlanner


class PopfPlanner(TyrPDDLPlanner):
    """The POPF planner wrapped into local PDDL planner."""

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

    def _get_engine_epsilon(self) -> Optional[Fraction]:
        return Fraction(1, 1000)

    def _get_computation_time(self, logs: List[LogMessage]) -> Optional[float]:
        for log in logs:
            for line in log.message.splitlines():
                if line.startswith("; Time"):
                    return float(line.split()[2])
        return None

    def _get_plan(self, proc_out: List[str]) -> str:
        plan: List[str] = []
        parsing = False
        for line in proc_out:
            if self._starting_plan_str() in line:
                parsing = True
                continue
            if not parsing:
                continue
            if self._ending_plan_str() == line:
                break
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
            return PlanGenerationResultStatus.SOLVED_SATISFICING
        if retval == 0:
            return PlanGenerationResultStatus.UNSOLVABLE_INCOMPLETELY
        return PlanGenerationResultStatus.INTERNAL_ERROR


__all__ = ["PopfPlanner"]
