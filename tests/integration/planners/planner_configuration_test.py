from typing import Tuple

import pytest

from tyr import Planner, get_all_planners
from tyr.problems.scanner import get_all_domains


class TestPlannerConfiguration:
    @pytest.mark.parametrize(
        ["planner", "problem"],
        [(p, pb) for p in get_all_planners() for pb in p.config.problems.items()],
        ids=lambda x: (
            x.name if isinstance(x, Planner) else x[0] if isinstance(x, tuple) else None
        ),
    )
    def test_real_planner_problems_configuration(
        self,
        planner: Planner,
        problem: Tuple[str, str],
    ):
        domain_name, version_name = problem
        domains = {d.name: d for d in get_all_domains()}
        assert domain_name in domains, f"The domain {domain_name} does not exist"
        domain = domains[domain_name]
        assert (
            version_name in domain.get_problem("01").versions
        ), f"The domain {domain_name} does not have the {version_name} version"
