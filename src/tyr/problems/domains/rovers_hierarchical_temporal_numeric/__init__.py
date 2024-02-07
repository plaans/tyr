from pathlib import Path
from typing import Optional

from unified_planning.shortcuts import AbstractProblem

from tyr.problems.converter import goals_to_tasks
from tyr.problems.domains.rovers_temporal_numeric import RoversTemporalNumericDomain
from tyr.problems.model import AbstractDomain, ProblemInstance


class RoversHierarchicalTemporalNumericDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return RoversTemporalNumericDomain().get_num_problems()

    def _build_problem_base(
        self, problem: ProblemInstance, version: str
    ) -> Optional[AbstractProblem]:
        base_tn = RoversTemporalNumericDomain().get_problem_version(
            problem.uid, version
        )
        if base_tn is None:
            return None
        mapping = {
            "communicated_soil_data": "get_soil_data",
            "communicated_rock_data": "get_rock_data",
            "communicated_image_data": "get_image_data",
        }
        freedom = {"rover": "free_to_recharge"}
        hier_dom_file = (Path(__file__).parent / "base/domain.hddl").resolve()
        return goals_to_tasks(base_tn, hier_dom_file, mapping, freedom)

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return self._build_problem_base(problem, "base")

    def build_problem_red(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return self._build_problem_base(problem, "red")

    def _build_problem_no_div(
        self, pb: ProblemInstance, version: str
    ) -> Optional[AbstractProblem]:
        base_tn = RoversTemporalNumericDomain().get_problem_version(pb.uid, version)
        if base_tn is None:
            return None
        mapping = {
            "communicated_soil_data": "get_soil_data",
            "communicated_rock_data": "get_rock_data",
            "communicated_image_data": "get_image_data",
        }
        freedom = {"rover": "free_to_recharge"}
        hier_dom_file = (Path(__file__).parent / "no_div/domain.hddl").resolve()
        return goals_to_tasks(base_tn, hier_dom_file, mapping, freedom)

    def build_problem_no_div(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        return self._build_problem_no_div(problem, "no_div")

    def build_problem_red_no_div(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        return self._build_problem_no_div(problem, "red_no_div")
