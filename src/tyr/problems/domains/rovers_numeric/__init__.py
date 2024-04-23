from pathlib import Path
from typing import Optional

from unified_planning.plans import Plan, PlanKind
from unified_planning.shortcuts import AbstractProblem

from tyr.problems.converter import reduce_version
from tyr.problems.model import AbstractDomain, ProblemInstance

FOLDER = Path(__file__).parent / "base"


class RoversNumericDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return len([f for f in FOLDER.iterdir() if "instance" in f.name])

    def get_quality_of_plan(
        self, plan: Plan, version: AbstractProblem
    ) -> Optional[float]:
        if plan.kind == PlanKind.SEQUENTIAL_PLAN:
            return len(list(a for a in plan.actions if a.action.name == "recharge"))
        if plan.kind == PlanKind.HIERARCHICAL_PLAN:
            return self.get_quality_of_plan(plan.action_plan, version)
        raise ValueError(f"Plan kind {plan.kind} is not supported.")

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return self.load_from_files(FOLDER, problem.uid)

    def build_problem_red(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return reduce_version(problem, "base", int(problem.uid) % 5 + 1)
