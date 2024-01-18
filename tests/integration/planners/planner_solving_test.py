import pytest

from tyr import Planner, get_all_planners
from tyr.planners.model.config import SolveConfig
from tyr.planners.model.result import PlannerResultStatus
from tyr.problems.scanner import get_all_domains


class TestPlannerSolving:
    @pytest.mark.slow
    @pytest.mark.parametrize(
        ["planner", "domain_name"],
        [(p, d) for p in get_all_planners() for d in list(p.config.problems.keys())],
        ids=lambda x: x.name if isinstance(x, Planner) else x,
    )
    def test_real_planner_solving(
        self,
        planner: Planner,
        domain_name: str,
    ):
        # Check solving the first instance does not return an error.
        domain = {d.name: d for d in get_all_domains()}[domain_name]
        problem_instance = domain.get_problem("01")
        solve_config = SolveConfig(memout=4 * 1024**3, timeout=1)
        result = planner.solve(problem_instance, solve_config)
        assert result.status != PlannerResultStatus.ERROR
