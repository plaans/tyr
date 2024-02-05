# pylint: disable = missing-class-docstring, missing-function-docstring

from pathlib import Path
from typing import Optional

from unified_planning.shortcuts import AbstractProblem

from tyr.problems.converter import goals_to_tasks
from tyr.problems.domains.satellite_temporal_numeric import (
    SatelliteTemporalNumericDomain,
)
from tyr.problems.model import AbstractDomain, ProblemInstance


class SatelliteHierarchicalTemporalNumericDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return SatelliteTemporalNumericDomain().get_num_problems()

    def _build_problem(
        self, problem: ProblemInstance, version: str
    ) -> Optional[AbstractProblem]:
        base_num = SatelliteTemporalNumericDomain().get_problem_version(
            problem.uid, version
        )
        if base_num is None:
            return None
        mapping = {
            "have_image": "do_observation",
            "pointing": "turn_to_abs",
        }
        hier_dom_file = (Path(__file__).parent / "base/domain.hddl").resolve()
        return goals_to_tasks(base_num, hier_dom_file, mapping)

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return self._build_problem(problem, "base")

    def build_problem_red(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return self._build_problem(problem, "red")

    def build_problem_no_float(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        return self._build_problem(problem, "no_float")

    def build_problem_red_no_float(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        return self._build_problem(problem, "red_no_float")
