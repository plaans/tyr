from pathlib import Path
from typing import Optional

from unified_planning.plans import Plan
from unified_planning.shortcuts import AbstractProblem

from tyr.problems.converter import goals_to_tasks
from tyr.problems.domains.rovers_numeric import RoversNumericDomain
from tyr.problems.model import AbstractDomain, ProblemInstance


class RoversHierarchicalNumericDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return RoversNumericDomain().get_num_problems()

    def get_quality_of_plan(
        self, plan: Plan, version: AbstractProblem
    ) -> Optional[float]:
        return RoversNumericDomain().get_quality_of_plan(plan, version)

    def _build_problem_base(
        self, problem: ProblemInstance, version: str
    ) -> Optional[AbstractProblem]:
        base_num = RoversNumericDomain().get_problem_version(problem.uid, version)
        if base_num is None:
            return None
        mapping = {
            "communicated_soil_data": "get_soil_data",
            "communicated_rock_data": "get_rock_data",
            "communicated_image_data": "get_image_data",
        }
        freedom = {"rover": "free_to_recharge"}
        hier_dom_file = (Path(__file__).parent / "base/domain.hddl").resolve()
        return goals_to_tasks(base_num, hier_dom_file, mapping, freedom)

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return self._build_problem_base(problem, "base")

    def build_problem_red(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return self._build_problem_base(problem, "red")
