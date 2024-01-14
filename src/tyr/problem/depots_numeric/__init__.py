# pylint: disable = missing-class-docstring, missing-function-docstring

from pathlib import Path
from typing import Optional

from unified_planning.shortcuts import AbstractProblem

from tyr.problem.model import AbstractDomain, ProblemInstance


class DepotsNumericDomain(AbstractDomain):
    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        folder = Path(__file__).parent / "base"
        return self.load_from_files(folder, problem.uid)
