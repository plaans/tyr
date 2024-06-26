from typing import Optional

from unified_planning.engines.mixins.compiler import CompilationKind
from unified_planning.shortcuts import AbstractProblem, Compiler

from tyr.problems.converter import scheduling_to_actions
from tyr.problems.domains.jobshop_scheduling import JobshopSchedulingDomain
from tyr.problems.model import AbstractDomain, ProblemInstance


class JobshopTemporalNumericDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return JobshopSchedulingDomain().get_num_problems()

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        schd = JobshopSchedulingDomain().get_problem_version(problem.uid, "base")
        if schd is None:
            return None
        return scheduling_to_actions(schd)

    def build_problem_no_neg_cond(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        base = problem.versions["base"].value
        if base is None:
            return None
        with Compiler(
            problem_kind=base.kind,
            compilation_kind=CompilationKind.NEGATIVE_CONDITIONS_REMOVING,
        ) as compiler:
            return compiler.compile(base).problem  # pylint: disable=no-member

    def build_problem_base_hier(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        from tyr.problems.domains.jobshop_scheduling import JobshopSchedulingDomain

        return JobshopSchedulingDomain().build_problem_base(problem)
