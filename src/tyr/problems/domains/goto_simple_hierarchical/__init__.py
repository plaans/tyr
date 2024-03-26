from pathlib import Path
from typing import Optional

from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.model.htn import HierarchicalProblem
from unified_planning.shortcuts import AbstractProblem

from tyr.problems.model import AbstractDomain, ProblemInstance


class GotoSimpleHierarchicalDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return 40

    def _from_base(
        self, problem: ProblemInstance, version: str
    ) -> Optional[AbstractProblem]:
        # Get the base version of the problem.
        base: HierarchicalProblem = problem.versions["base"].value
        if base is None:
            return None

        # Create the new domain.
        domain_file = Path(__file__).parent / version / "domain.hddl"
        pb: HierarchicalProblem = PDDLReader().parse_problem(domain_file.as_posix())

        # Add all objects.
        pb.add_objects(base.all_objects)

        # Initialize all state variables.
        for sv, val in base.explicit_initial_values.items():
            pb.set_initial_value(pb.fluent(sv.fluent().name)(*sv.args), val)

        # Add the goals.
        for task in base.task_network.subtasks:
            pb.task_network.add_subtask(task)

        return pb

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        domain_file = Path(__file__).parent / "base" / "domain.hddl"
        pb: HierarchicalProblem = PDDLReader().parse_problem(domain_file.as_posix())

        roads = [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 5), (4, 5)]
        positions = set().union(*roads)

        # Types
        position_type = pb.user_type("position")
        truck_type = pb.user_type("truck")

        # Objects
        for position in positions:
            pb.add_object(f"P{position}", position_type)
        pb.add_object("T1", truck_type)

        # Initial values
        for road in roads:
            source = pb.object(f"P{road[0]}")
            target = pb.object(f"P{road[1]}")
            pb.set_initial_value(pb.fluent("road")(source, target), True)
            pb.set_initial_value(pb.fluent("road")(target, source), True)
        pb.set_initial_value(pb.fluent("at")(pb.object("T1"), pb.object("P1")), True)

        # Goals
        multiplier = 1 if int(problem.uid) > 30 else 10
        offset = -30 if int(problem.uid) > 30 else 0
        for _ in range(int(problem.uid) * multiplier + offset):
            pb.task_network.add_subtask(
                pb.get_task("goto"), pb.object("T1"), pb.object("P5")
            )

        return pb

    def build_problem_exponential(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        return problem.versions["base"].value

    def build_problem_linear(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        return self._from_base(problem, "linear")

    def build_problem_insertion(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        pb = self._from_base(problem, "insertion")
        if pb is None:
            return pb

        # Add the free-move task for task insertion.
        pb.task_network.add_subtask(pb.get_task("free-move"), pb.object("T1"))
        return pb
