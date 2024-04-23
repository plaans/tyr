from math import ceil
from pathlib import Path
from typing import Optional

from unified_planning.plans import Plan, PlanKind, SequentialPlan
from unified_planning.shortcuts import AbstractProblem, Problem

from tyr.problems.converter import reduce_version
from tyr.problems.model import AbstractDomain, ProblemInstance

FOLDER = Path(__file__).parent / "base"


class SatelliteNumericDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return len([f for f in FOLDER.iterdir() if "instance" in f.name])

    def get_quality_of_plan(self, plan: Plan, version: Problem) -> Optional[float]:
        if plan.kind == PlanKind.SEQUENTIAL_PLAN:
            quality = 0
            slew_time = version.fluent("slew_time")
            for action in plan.actions:
                if action.action.name != "turn_to":
                    continue
                val = version.initial_value(slew_time(*action.actual_parameters[1:]))
                quality += val.constant_value()
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

    def build_problem_no_float(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        # Get the base version of the problem.
        base = problem.versions["base"].value
        if base is None:
            return None

        # Round all real values to get integers
        no_float = base.clone()
        for sv, value in base.explicit_initial_values.items():
            if value.is_real_constant():
                no_float.set_initial_value(sv, ceil(value.real_constant_value()))
        return no_float

    def build_problem_red_no_float(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        return reduce_version(problem, "no_float", int(problem.uid) % 5 + 1)
