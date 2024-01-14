# pylint: disable = missing-class-docstring, missing-function-docstring

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Optional

from unified_planning.io import PDDLReader
from unified_planning.shortcuts import AbstractProblem

from tyr.problem.model import AbstractDomain, ProblemInstance


class DepotsTemporalNumericDomain(AbstractDomain):
    def build_problem_base(self, problem: ProblemInstance) -> Optional[AbstractProblem]:
        folder = Path(__file__).parent / "base"
        return self.load_from_files(folder, problem.uid)

    def build_problem_no_div(
        self, problem: ProblemInstance
    ) -> Optional[AbstractProblem]:
        # Get the base version of the problem.
        base = problem.versions["base"].value
        if base is None:
            return None

        # Load the domain of the no_div version from a PDDL file.
        no_div = PDDLReader().parse_problem(
            (Path(__file__).parent / "no_div/domain.pddl").resolve().as_posix()
        )

        # Add all objects.
        no_div.add_objects(base.all_objects)

        # Initialize all state variable not involved in a division
        # and save skipped one in a map for future access.
        saved_values: Dict[str, Dict[tuple, Any]] = defaultdict(dict)
        for sv, value in base.explicit_initial_values.items():
            fluent = sv.fluent()
            if fluent.name in ["speed", "distance", "weight", "power"]:
                saved_values[fluent.name][tuple(map(str, sv.args))] = value
            else:
                no_div.set_initial_value(no_div.fluent(fluent.name)(*sv.args), value)

        # Replace state variables involved in a division by static ones.
        for x in no_div.objects(no_div.user_type("truck")):
            for y in no_div.objects(no_div.user_type("place")):
                for z in no_div.objects(no_div.user_type("place")):
                    sv = no_div.fluent("drive_duration")(x, y, z)
                    distance = saved_values["distance"][(y.name, z.name)]
                    speed = saved_values["speed"][(x.name,)]
                    value = int(distance.constant_value() / speed.constant_value() * 10)
                    no_div.set_initial_value(sv, value)

        for x in no_div.objects(no_div.user_type("hoist")):
            for y in no_div.objects(no_div.user_type("crate")):
                sv = no_div.fluent("load_duration")(x, y)
                weight = saved_values["weight"][(y.name,)]
                power = saved_values["power"][(x.name,)]
                value = int(weight.constant_value() / power.constant_value() * 10)
                no_div.set_initial_value(sv, value)

        # Add all goals.
        for x in base.goals:
            no_div.add_goal(x)

        # Add the metrics.
        for x in base.quality_metrics:
            no_div.add_quality_metric(x)

        return no_div
