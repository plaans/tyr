import signal

import pytest

from tyr.planners.model.config import RunningMode, SolveConfig
from tyr.planners.model.planner import Planner
from tyr.planners.scanner import get_all_planners
from tyr.problems.model.domain import AbstractDomain
from tyr.problems.scanner import get_all_domains


class TestResolution:
    @pytest.mark.slow
    @pytest.mark.parametrize("planner", get_all_planners(), ids=lambda x: x.name)
    @pytest.mark.parametrize("domain", get_all_domains(), ids=lambda x: x.name)
    def test_real_resolution(self, planner: Planner, domain: AbstractDomain):
        config = SolveConfig(
            jobs=1,
            memout=4 * 1024**3,
            timeout=10,
            timeout_offset=0,
            db_only=False,
            no_db_load=True,
            no_db_save=True,
            unify_epsilons=False,
        )
        problem = domain.get_problem("1")
        assert problem is not None
        planner.solve(problem, config, RunningMode.ONESHOT)  # Check no crash
        signal.alarm(0)  # Disable potential timeout
