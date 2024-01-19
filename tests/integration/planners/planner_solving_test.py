import pytest

from tyr import (
    Planner,
    PlannerResultStatus,
    SolveConfig,
    get_all_domains,
    get_all_planners,
    register_all_planners,
)

SUCCESS_PLANNER = {p.name: False for p in get_all_planners()}


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
        register_all_planners()
        # Check solving the first instance does not return an error.
        domain = {d.name: d for d in get_all_domains()}[domain_name]
        problem_instance = domain.get_problem("01")
        solve_config = SolveConfig(memout=4 * 1024**3, timeout=1)
        rejected_status = [PlannerResultStatus.ERROR, PlannerResultStatus.UNSUPPORTED]
        result = planner.solve(problem_instance, solve_config)
        assert result.status not in rejected_status
        if result.status == PlannerResultStatus.SOLVED:
            SUCCESS_PLANNER[planner.name] = True

    @pytest.mark.slow
    @pytest.mark.run(after="test_real_planner_solving")
    @pytest.mark.parametrize("planner", get_all_planners(), ids=lambda x: x.name)
    def test_at_least_one_problem_solved(self, planner: Planner):
        # Ensure one planner has been solved so a full success process has been done.
        assert SUCCESS_PLANNER[planner.name] is True
