import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, List, Optional

from unified_planning.engines.results import LogMessage, PlanGenerationResultStatus
from unified_planning.plans import Plan
from unified_planning.shortcuts import AbstractProblem, Problem

from tyr.planners.model.pddl_planner import TyrPDDLPlanner


class OpticPlanner(TyrPDDLPlanner):
    """The Optic planner wrapped into local PDDL planner."""

    def _get_cmd(
        self,
        domain_filename: str,
        problem_filename: str,
        plan_filename: str,
    ) -> List[str]:
        binary = (Path(__file__).parent / "optic-cplex").resolve().as_posix()
        return f"{binary} {domain_filename} {problem_filename} -N".split()

    def _get_engine_epsilon(self) -> Optional[Fraction]:
        return Fraction(1, 1000)

    def _get_plan(self, proc_out: List[str]) -> str:
        sol_found = "; Time"
        sol_idx = -1
        for idx, line in enumerate(proc_out):
            if sol_found in line:
                sol_idx = idx
                break
        if sol_idx == -1:
            # No solution
            plan = []
        else:
            # Keep only the plan with the time
            plan = proc_out[sol_idx:]
            try:
                plan = plan[: plan.index("\n")]
            except ValueError:
                pass
        return "\n".join(plan)

    def _result_status(
        self,
        problem: Problem,
        plan: Optional[Any],
        retval: int,
        log_messages: Optional[List[LogMessage]] = None,
    ) -> PlanGenerationResultStatus:
        print(log_messages)
        if plan is not None:
            return PlanGenerationResultStatus.SOLVED_SATISFICING
        if retval == 0:
            return PlanGenerationResultStatus.UNSOLVABLE_INCOMPLETELY
        return PlanGenerationResultStatus.INTERNAL_ERROR
