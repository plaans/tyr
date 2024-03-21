from typing import Optional

from unified_planning.shortcuts import AbstractProblem

from tyr.problems.domains.goto_simple_hierarchical import GotoSimpleHierarchicalDomain
from tyr.problems.model import AbstractDomain, ProblemInstance


class GotoComplexHierarchicalDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return GotoSimpleHierarchicalDomain().get_num_problems()

    def _from_simple(
        self, problem: ProblemInstance, version: str
    ) -> Optional[AbstractProblem]:
        base = GotoSimpleHierarchicalDomain().get_problem_version(problem.uid, version)
        if base is None:
            return None

        # Create the new domain.
        pb = base.clone()
        pb.name = "complex_goto"

        # Add the goals.
        for _ in range(int(problem.uid) * 10):
            pb.task_network.add_subtask(
                pb.get_task("goto"), pb.object("T1"), pb.object("P3")
            )

        return pb

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return self._from_simple(problem, "base")

    def build_problem_exponential(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        return problem.versions["base"].value

    def build_problem_linear(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        return self._from_simple(problem, "linear")

    def build_problem_insertion(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        return self._from_simple(problem, "insertion")
