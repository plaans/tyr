# pylint: disable = missing-class-docstring, missing-function-docstring

from pathlib import Path
from typing import Optional

from unified_planning.shortcuts import AbstractProblem

from tyr.problem.converter import goals_to_tasks
from tyr.problem.depots_numeric import DepotsNumericDomain
from tyr.problem.model import AbstractDomain, ProblemInstance


class DepotsHierarchicalNumericDomain(AbstractDomain):
    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        base_num = DepotsNumericDomain().get_problem_version(problem.uid, "base")
        if base_num is None:
            return None
        mapping = {"on": "do_put_on"}
        hier_dom_file = (Path(__file__).parent / "base/domain.hddl").resolve()
        return goals_to_tasks(base_num, hier_dom_file, mapping)
