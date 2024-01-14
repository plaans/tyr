# pylint: disable = missing-class-docstring, missing-function-docstring

from pathlib import Path
from typing import Optional

from unified_planning.shortcuts import AbstractProblem

from tyr.problem.converter import goals_to_tasks
from tyr.problem.depots_numeric import DepotsNumericDomain
from tyr.problem.model import AbstractDomain, ProblemInstance


class DepotsHierarchicalNumericDomain(AbstractDomain):
    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        num_problem = DepotsNumericDomain().get_problem(problem.uid)
        if num_problem is None:  # pragma: no cover
            return None
        base_tn = num_problem.versions["base"].value
        if base_tn is None:
            return None

        mapping = {"on": "do_put_on"}
        hier_dom_file = (Path(__file__).parent / "base/domain.hddl").resolve()
        return goals_to_tasks(base_tn, hier_dom_file, mapping)
