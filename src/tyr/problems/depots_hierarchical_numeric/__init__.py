# pylint: disable = missing-class-docstring, missing-function-docstring

from pathlib import Path
from typing import Optional

from unified_planning.shortcuts import AbstractProblem

from tyr.problems.converter import goals_to_tasks
from tyr.problems.depots_numeric import DepotsNumericDomain
from tyr.problems.model import AbstractDomain, ProblemInstance


class DepotsHierarchicalNumericDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return DepotsNumericDomain().get_num_problems()

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        base_num = DepotsNumericDomain().get_problem_version(problem.uid, "base")
        if base_num is None:
            return None
        mapping = {"on": "do_put_on"}
        hier_dom_file = (Path(__file__).parent / "base/domain.hddl").resolve()
        return goals_to_tasks(base_num, hier_dom_file, mapping)
