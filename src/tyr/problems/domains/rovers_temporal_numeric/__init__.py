from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Optional

from unified_planning.io import PDDLReader
from unified_planning.shortcuts import AbstractProblem

from tyr.problems.converter import reduce_version
from tyr.problems.model import AbstractDomain, ProblemInstance

FOLDER = Path(__file__).parent / "base"


class RoversTemporalNumericDomain(AbstractDomain):
    def get_num_problems(self) -> int:
        return len([f for f in FOLDER.iterdir() if "instance" in f.name])

    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return self.load_from_files(FOLDER, problem.uid)

    def build_problem_red(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        return reduce_version(problem, "base", int(problem.uid) % 5 + 1)

    def build_problem_fix_dur(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        return self.load_from_files(FOLDER.parent / "fix_dur", problem.uid)

    def build_problem_red_fix_dur(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        return reduce_version(problem, "fix_dur", int(problem.uid) % 5 + 1)

    def build_problem_no_div(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        # Get the base version of the problem.
        base = problem.versions["fix_dur"].value
        if base is None:
            return None

        # Load the domain of the no_div version from a PDDL file.
        no_div = PDDLReader().parse_problem(
            (Path(__file__).parent / "no_div/domain.hddl").resolve().as_posix()
        )

        # Add all objects.
        no_div.add_objects(base.all_objects)

        # Initialize all state variable not involved in a division
        # and save skipped one in a map for future access.
        saved_values: Dict[str, Dict[tuple, Any]] = defaultdict(dict)
        for sv, value in base.explicit_initial_values.items():
            fluent = sv.fluent()
            if fluent.name in ["energy", "recharge-rate"]:
                saved_values[fluent.name][tuple(map(str, sv.args))] = value
            else:
                no_div.set_initial_value(no_div.fluent(fluent.name)(*sv.args), value)

        # Replace state variables involved in a division by static ones.
        for x in no_div.objects(no_div.user_type("rover")):
            energy = saved_values["energy"][(x.name,)]
            rate = saved_values["recharge-rate"][(x.name,)]
            # pylint: disable=eval-used
            atom = int(round(eval(str(1 / rate * 100))))  # nosec: B307
            for multi, suffix in [
                (energy, ""),
                (80, "-max"),
                *((i, f"-{i}") for i in range(1, 9) if i != 7),
            ]:
                sv = no_div.fluent(f"recharge-duration{suffix}")(x)
                value = atom * multi
                no_div.set_initial_value(sv, value)

        # Add all goals.
        for x in base.goals:
            no_div.add_goal(x)

        # Add the metrics.
        for x in base.quality_metrics:
            no_div.add_quality_metric(x)

        return no_div

    def build_problem_red_no_div(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        return reduce_version(problem, "no_div", int(problem.uid) % 5 + 1)
