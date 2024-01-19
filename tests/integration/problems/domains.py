from pathlib import Path
from typing import Optional

from unified_planning.shortcuts import AbstractProblem

from tyr import AbstractDomain, ProblemInstance


class FakeDomain(AbstractDomain):
    """A fake domain used for demonstration."""

    def get_num_problems(self) -> int:
        return 3

    def build_problem_a_first(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        """
        Builds the 'a_first' version of problem.

        It is used to demonstrate that even if the version name is before the
        'base' one in alphabetical order, it can ued since the values are lazy.
        """
        base_problem = problem.versions["base"].value
        if base_problem is None:
            return None
        base_problem.name = "First version in alphabetical order"
        return base_problem

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        """
        Builds the 'base' version of problem.

        It is used to demonstrate the creation of problems from files.
        """
        folder_path = Path(__file__).parent / "hddl"
        return self.load_from_files(folder_path, problem.uid)

    def build_problem_modified(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        """
        Builds the 'modified' version of problem.

        It is used to demonstrate how to modify an other version of the problem to create a new one.
        """
        base_problem = problem.versions["base"].value
        if base_problem is None:
            return None
        # Make the modifications
        base_problem.name = "Modified name"
        return base_problem
