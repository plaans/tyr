from typing import Optional

from unified_planning.model.htn import HierarchicalProblem, TaskNetwork
from unified_planning.shortcuts import AbstractProblem

from tyr.problems.domains.goto_simple_hierarchical import GotoSimpleHierarchicalDomain
from tyr.problems.model import AbstractDomain, ProblemInstance


class GotoHardHierarchicalDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return GotoSimpleHierarchicalDomain().get_num_problems()

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        base = GotoSimpleHierarchicalDomain().get_problem_version(problem.uid, "base")
        if base is None:
            return None

        # Create the new domain.
        pb = base.clone()
        pb.name = "hard_goto"

        # Set the goals.
        pb._initial_task_network = TaskNetwork()  # pylint: disable=protected-access
        for _ in range(int(problem.uid) * 5):
            for pos in ["P3", "P4", "P5"]:
                pb.task_network.add_subtask(
                    pb.get_task("goto"), pb.object("T1"), pb.object(pos)
                )

        return pb

    def build_problem_exponential(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        return problem.versions["base"].value

    def build_problem_linear(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        base = GotoSimpleHierarchicalDomain().get_problem_version(problem.uid, "linear")
        if base is None:
            return None

        # Create the new domain.
        pb = base.clone()
        pb.name = "hard_goto"

        # Set the goals.
        pb._initial_task_network = TaskNetwork()  # pylint: disable=protected-access
        for _ in range(int(problem.uid) * 5):
            for pos in ["P3", "P4", "P5"]:
                pb.task_network.add_subtask(
                    pb.get_task("goto"), pb.object("T1"), pb.object(pos)
                )

        return pb

    def build_problem_insertion(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        base = GotoSimpleHierarchicalDomain().get_problem_version(
            problem.uid, "insertion"
        )
        if base is None:
            return None

        # Create the new domain.
        pb = base.clone()
        pb.name = "hard_goto"

        # Set the goals.
        pb._initial_task_network = TaskNetwork()  # pylint: disable=protected-access
        for _ in range(int(problem.uid) * 5):
            for pos in ["P3", "P4", "P5"]:
                pb.task_network.add_subtask(
                    pb.get_task("aim"), pb.object("T1"), pb.object(pos)
                )

        # Add the free-move task for task insertion.
        pb.task_network.add_subtask(pb.get_task("free-move"), pb.object("T1"))

        return pb
