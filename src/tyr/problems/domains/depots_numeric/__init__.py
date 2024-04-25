from pathlib import Path
from typing import Optional

from unified_planning.plans import Plan, PlanKind, SequentialPlan
from unified_planning.shortcuts import AbstractProblem

from tyr.problems.converter import reduce_version
from tyr.problems.model import AbstractDomain, ProblemInstance

FOLDER = Path(__file__).parent / "base"


class DepotsNumericDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return len([f for f in FOLDER.iterdir() if "instance" in f.name])

    def get_quality_of_plan(
        self, plan: Plan, version: AbstractProblem
    ) -> Optional[float]:
        if plan.kind == PlanKind.SEQUENTIAL_PLAN:
            quality = 0
            for action in plan.actions:
                if action.action.name.lower() == "lift":
                    quality += 1
                if action.action.name.lower() == "drive":
                    quality += 10
            return quality
        if plan.kind == PlanKind.TIME_TRIGGERED_PLAN:
            seq_plan = SequentialPlan(list(a for (_, a, _) in plan.timed_actions))
            return self.get_quality_of_plan(seq_plan, version)
        if plan.kind == PlanKind.HIERARCHICAL_PLAN:
            return self.get_quality_of_plan(plan.action_plan, version)
        raise ValueError(f"Plan kind {plan.kind} is not supported.")

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return self.load_from_files(FOLDER, problem.uid)

    def build_problem_red(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return reduce_version(problem, "base", int(problem.uid) % 5 + 1)

    def build_problem_base_hier(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        from tyr.problems.domains.depots_hierarchical_numeric import (
            DepotsHierarchicalNumericDomain,
        )

        return DepotsHierarchicalNumericDomain().build_problem_base(problem)

    def build_problem_red_hier(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        from tyr.problems.domains.depots_hierarchical_numeric import (
            DepotsHierarchicalNumericDomain,
        )

        return DepotsHierarchicalNumericDomain().build_problem_red(problem)
