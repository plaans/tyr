import resource
import time
from dataclasses import replace
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

from tests.utils import ModelTest
from tyr import (
    AbstractDomain,
    Planner,
    PlannerConfig,
    PlannerResult,
    ProblemInstance,
    SolveConfig,
)
from tyr.core.constants import LOGS_DIR
from tyr.planner.model.result import PlannerResultStatus


class MockdomainDomain(AbstractDomain):
    def build_problem_base(self, problem: ProblemInstance):
        result = MagicMock()
        result.uid = problem.uid * 3
        return result


class TestPlanner(ModelTest):
    # ============================================================================ #
    #                                    Getters                                   #
    # ============================================================================ #

    def get_default_attributes(self) -> Dict[str, Any]:
        return {"_config": self.config()}

    def get_instance(self) -> Any:
        return Planner(self.config())

    def config(self) -> PlannerConfig:
        return PlannerConfig(name="mock-config", problems={"mockdomain": "base"})

    @pytest.fixture()
    def planner(self):
        yield self.get_instance()

    @staticmethod
    @pytest.fixture()
    def mocked_planner():
        yield Mock(Planner)

    @staticmethod
    @pytest.fixture()
    def domain():
        yield MockdomainDomain()

    @staticmethod
    @pytest.fixture()
    def problem(domain: AbstractDomain):
        yield domain.get_problem("01")

    @staticmethod
    @pytest.fixture()
    def solve_config() -> SolveConfig:
        yield SolveConfig(
            memout=4 * 1024 * 1024 * 1024,  # 4GB
            timeout=350,
        )

    # ============================================================================ #
    #                                     Tests                                    #
    # ============================================================================ #

    # =============================== Get log file =============================== #

    @pytest.mark.parametrize("problem_id", ["01", "06"])
    @pytest.mark.parametrize("domain_name", ["domain1", "domain2"])
    @pytest.mark.parametrize("planner_name", ["planner1", "planner2"])
    def test_get_log_file(
        self,
        planner: Planner,
        problem: ProblemInstance,
        planner_name: str,
        domain_name: str,
        problem_id: str,
    ):
        old_config = planner.config
        old_uid = problem.uid
        old_name = problem.domain.name

        planner._config = replace(planner.config, name=planner_name)
        problem._uid = problem_id
        problem.domain._name = domain_name

        expected = LOGS_DIR / planner_name / domain_name / problem_id / "solve.log"
        result = planner.get_log_file(problem)
        assert result == expected

        planner._config = old_config
        problem._uid = old_uid
        problem.domain._name = old_name

    # ================================ Get version =============================== #

    def test_get_correct_version(self, planner: Planner, problem: ProblemInstance):
        version = planner.get_version(problem)
        assert version.uid == problem.uid * 3

    def test_get_inexistant_version(self, planner: Planner, problem: ProblemInstance):
        planner.config.problems["mockdomain"] = "inexistant"
        version = planner.get_version(problem)
        assert version is None

    def test_get_version_from_unsupported_domain(
        self, planner: Planner, problem: ProblemInstance
    ):
        planner.config.problems.clear()
        version = planner.get_version(problem)
        assert version is None

    # =================================== Solve ================================== #

    def test_solve_get_version(
        self,
        mocked_planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        mocked_planner.solve = lambda x, y: Planner.solve(mocked_planner, x, y)
        try:
            mocked_planner.solve(problem, solve_config)
        except Exception:  # nosec: B110
            pass
        mocked_planner.get_version.assert_called_once_with(problem)

    def test_solve_no_available_versiom(
        self,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        planner.config.problems.clear()
        expected = PlannerResult.unsupported(problem, planner)
        result = planner.solve(problem, solve_config)
        assert result == expected

    @pytest.mark.parametrize("timeout", [0, 15, 6])
    @patch("unified_planning.shortcuts.OneshotPlanner", autospec=True)
    def test_solve_using_upf(
        self,
        mocked_oneshot_planner: Mock,
        timeout: int,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        solve_config = replace(solve_config, timeout=timeout)
        mocked_planner = mocked_oneshot_planner.return_value.__enter__.return_value
        version = planner.get_version(problem)

        try:
            planner.solve(problem, solve_config)
        except Exception:  # nosec: B110
            pass

        mocked_oneshot_planner.assert_called_once_with(name=planner.name)
        mocked_planner.solve.assert_called_once()
        solve_args, solve_kwargs = mocked_planner.solve.call_args
        assert solve_args == (version,)
        assert len(solve_kwargs) == 2
        assert solve_kwargs["timeout"] == timeout
        assert (
            solve_kwargs["output_stream"].name
            == planner.get_log_file(problem).as_posix()
        )

    @patch("unified_planning.shortcuts.OneshotPlanner", autospec=True)
    @patch("tyr.planner.model.planner.PlannerResult.from_upf", autospec=True)
    def test_solve_result_from_upf(
        self,
        mocked_result_from_upf: Mock,
        mocked_oneshot_planner: Mock,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        upf_result = (
            mocked_oneshot_planner.return_value.__enter__.return_value.solve.return_value
        )
        mocked_result_from_upf.return_value.computation_time = 0

        result = planner.solve(problem, solve_config)
        mocked_result_from_upf.assert_called_once_with(problem, upf_result)
        assert result == mocked_result_from_upf.return_value

    @pytest.mark.parametrize("computation_time", [1, 10, 15.7])
    @patch("unified_planning.shortcuts.OneshotPlanner", autospec=True)
    def test_solve_error(
        self,
        mocked_oneshot_planner: Mock,
        computation_time: float,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        mocked_planner = mocked_oneshot_planner.return_value.__enter__.return_value
        mocked_planner.solve.side_effect = RuntimeError
        expected = PlannerResult.error(problem, planner, computation_time)
        with patch("time.time", side_effect=[0, 0, computation_time]):
            result = planner.solve(problem, solve_config)
        assert result == expected

    @pytest.mark.parametrize("computation_time", [1, 10, 15.7])
    @patch("unified_planning.shortcuts.OneshotPlanner", autospec=True)
    @patch("tyr.planner.model.planner.PlannerResult.from_upf", autospec=True)
    def test_solve_computation_time(
        self,
        mocked_result_from_upf: Mock,
        mocked_oneshot_planner: Mock,
        computation_time: float,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        upf_result = PlannerResult(planner.name, problem, PlannerResultStatus.SOLVED)
        mocked_result_from_upf.return_value = upf_result
        expected = replace(upf_result, computation_time=computation_time)
        with patch("time.time", side_effect=[0, 0, computation_time]):
            result = planner.solve(problem, solve_config)
        assert result == expected

    @pytest.mark.timeout(3)
    @pytest.mark.parametrize("timeout", [1, 2])
    @patch("unified_planning.shortcuts.OneshotPlanner", autospec=True)
    def test_solve_timeout(
        self,
        mocked_oneshot_planner: Mock,
        timeout: int,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        def solve(*args, **kwargs):
            time.sleep(timeout + 10)

        solve_config = replace(solve_config, timeout=timeout)
        mocked_planner = mocked_oneshot_planner.return_value.__enter__.return_value
        mocked_planner.solve.side_effect = solve

        expected = PlannerResult.timeout(problem, planner, timeout)
        result = planner.solve(problem, solve_config)
        assert result == expected

    @pytest.mark.parametrize("timeout", [10, 200])
    @patch("unified_planning.shortcuts.OneshotPlanner", autospec=True)
    @patch("tyr.planner.model.planner.PlannerResult.from_upf", autospec=True)
    def test_solve_crop_to_timeout(
        self,
        mocked_result_from_upf: Mock,
        mocked_oneshot_planner: Mock,
        timeout: int,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        solve_config = replace(solve_config, timeout=timeout)
        upf_result = PlannerResult(
            planner.name,
            problem,
            PlannerResultStatus.SOLVED,
            computation_time=2 * timeout,
        )
        mocked_result_from_upf.return_value = upf_result

        expected = PlannerResult.timeout(problem, planner, timeout)
        result = planner.solve(problem, solve_config)
        assert result == expected

    @pytest.mark.parametrize("memout", [10, 200])
    @patch("resource.setrlimit")
    def test_solve_memout(
        self,
        mock_resource: Mock,
        memout: int,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        solve_config = replace(solve_config, memout=memout)
        planner.solve(problem, solve_config)
        mock_resource.assert_called_once_with(
            resource.RLIMIT_AS, (memout, resource.RLIM_INFINITY)
        )
