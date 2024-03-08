from pathlib import Path
from typing import Optional, Union

from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.model.htn import HierarchicalProblem
from unified_planning.shortcuts import AbstractProblem, Problem

from tyr.problems.model import AbstractDomain, ProblemInstance


class SimpleGotoHierarchicalDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return 30

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        domain_file = Path(__file__).parent / "base" / "domain.hddl"
        pb = PDDLReader().parse_problem(domain_file.as_posix())

        roads = [
            (1, 2),
            (1, 5),
            (2, 3),
            (2, 4),
            (3, 4),
            (3, 7),
            (5, 6),
            (2, 8),
            (4, 8),
            (5, 9),
            (8, 9),
            (1, 9),
            (6, 10),
            (4, 10),
            (5, 10),
            (7, 10),
            (5, 11),
            (4, 11),
            (9, 11),
            (10, 11),
            (4, 12),
            (3, 12),
            (12, 13),
            (7, 13),
            (4, 13),
            (9, 14),
            (1, 14),
            (2, 14),
            (8, 14),
            (6, 7),
        ]
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
        for _ in range(int(problem.uid) * 10):
            pb.task_network.add_subtask(
                pb.get_task("goto"), pb.object("T1"), pb.object("P12")
            )

        return pb

    def build_problem_linear(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        # Get the base version of the problem.
        base: HierarchicalProblem = problem.versions["base"].value
        if base is None:
            return None

        # Create the new domain.
        domain_file = Path(__file__).parent / "linear" / "domain.hddl"
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
