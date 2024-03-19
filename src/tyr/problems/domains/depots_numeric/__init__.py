from pathlib import Path
from typing import Optional

from unified_planning.shortcuts import AbstractProblem

from tyr.problems.converter import get_goals, reduce_version
from tyr.problems.model import AbstractDomain, ProblemInstance

FOLDER = Path(__file__).parent / "base"


class DepotsNumericDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return len([f for f in FOLDER.iterdir() if "instance" in f.name])

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return self.load_from_files(FOLDER, problem.uid)

    def build_problem_red(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return reduce_version(problem, "base", int(problem.uid) % 5 + 1)