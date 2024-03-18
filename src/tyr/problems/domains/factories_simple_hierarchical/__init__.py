from pathlib import Path
from typing import Optional

from unified_planning.io.pddl_reader import PDDLReader
from unified_planning.shortcuts import AbstractProblem

from tyr.problems.model import AbstractDomain, ProblemInstance

FOLDER = Path(__file__).parent / "base"


class FactoriesSimpleHierarchicalDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return len([f for f in FOLDER.iterdir() if "instance" in f.name])

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return self.load_from_files(FOLDER, problem.uid)

    def build_problem_exponential(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        return problem.versions["base"].value

    def build_problem_linear(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        # Get the base version of the problem.
        base = problem.versions["exponential"].value
        if base is None:
            return None

        # Create the new domain.
        domain_file = Path(__file__).parent / "linear" / "domain.hddl"
        pb = PDDLReader().parse_problem(domain_file.as_posix())

        # Add all objects.
        pb.add_objects(base.all_objects)

        # Initialize all state variables.
        for sv, val in base.explicit_initial_values.items():
            pb.set_initial_value(pb.fluent(sv.fluent().name)(*sv.args), val)

        # Add the goals.
        for task in base.task_network.subtasks:
            pb.task_network.add_subtask(task)

        return pb

    def build_problem_insertion(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        # Get the base version of the problem.
        base = problem.versions["exponential"].value
        if base is None:
            return None

        # Create the new domain.
        domain_file = Path(__file__).parent / "insertion" / "domain.hddl"
        pb = PDDLReader().parse_problem(domain_file.as_posix())

        # Add all objects.
        pb.add_objects(base.all_objects)

        # Initialize all state variables.
        for sv, val in base.explicit_initial_values.items():
            pb.set_initial_value(pb.fluent(sv.fluent().name)(*sv.args), val)

        # Add the goals.
        for task in base.task_network.subtasks:
            # Convert the goto task into a at goal.
            if task.task.name == "goto":
                pb.add_goal(pb.fluent("truck-at")(task.parameters[0]))
            else:
                pb.task_network.add_subtask(task)

        # Add the free-drive task for task insertion.
        pb.task_network.add_subtask(pb.get_task("free-move"))

        return pb
