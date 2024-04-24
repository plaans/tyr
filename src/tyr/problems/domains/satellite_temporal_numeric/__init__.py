from math import ceil
from pathlib import Path
from typing import Optional

from unified_planning.shortcuts import AbstractProblem

from tyr.problems.converter import reduce_version
from tyr.problems.model import AbstractDomain, ProblemInstance

FOLDER = Path(__file__).parent / "base"


class SatelliteTemporalNumericDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return len([f for f in FOLDER.iterdir() if "instance" in f.name])

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return self.load_from_files(FOLDER, problem.uid)

    def build_problem_red(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return reduce_version(problem, "base", int(problem.uid) % 5 + 1)

    def build_problem_no_float(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        # Get the base version of the problem.
        base = problem.versions["base"].value
        if base is None:
            return None

        # Round all real values to get integers
        no_float = base.clone()
        for sv, value in base.explicit_initial_values.items():
            if value.is_real_constant():
                no_float.set_initial_value(sv, ceil(value.real_constant_value()))
        return no_float

    def build_problem_red_no_float(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        return reduce_version(problem, "no_float", int(problem.uid) % 5 + 1)

    def build_problem_base_hier(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        from tyr.problems.domains.satellite_hierarchical_temporal_numeric import (
            SatelliteHierarchicalTemporalNumericDomain,
        )

        return SatelliteHierarchicalTemporalNumericDomain().build_problem_base(problem)

    def build_problem_red_hier(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        from tyr.problems.domains.satellite_hierarchical_temporal_numeric import (
            SatelliteHierarchicalTemporalNumericDomain,
        )

        return SatelliteHierarchicalTemporalNumericDomain().build_problem_red(problem)

    def build_problem_no_float_hier(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        from tyr.problems.domains.satellite_hierarchical_temporal_numeric import (
            SatelliteHierarchicalTemporalNumericDomain,
        )

        return SatelliteHierarchicalTemporalNumericDomain().build_problem_no_float(
            problem
        )

    def build_problem_red_no_float_hier(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        from tyr.problems.domains.satellite_hierarchical_temporal_numeric import (
            SatelliteHierarchicalTemporalNumericDomain,
        )

        return SatelliteHierarchicalTemporalNumericDomain().build_problem_red_no_float(
            problem
        )
