import os
import resource
import time
import traceback
from dataclasses import replace
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, call, patch

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
from tyr.core.paths import TyrPaths
from tyr.planners.database import Database
from tyr.planners.model.config import RunningMode
from tyr.planners.model.result import PlannerResultStatus


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
        return {"_config": self.config(), "_last_upf_result": None}

    def get_instance(self) -> Any:
        return Planner(self.config())

    def config(self) -> PlannerConfig:
        return PlannerConfig(
            name="mock-config",
            anytime_name="mock-anytime",
            oneshot_name="mock-oneshot",
            problems={"mockdomain": "base"},
            env={"MY_VARIABLE": "new_value", "MY_BOOL": "True"},
        )

    @pytest.fixture()
    def planner(self):
        yield self.get_instance()

    @staticmethod
    @pytest.fixture()
    def mock_planner():
        yield Mock(Planner)

    @staticmethod
    @pytest.fixture()
    def domain():
        yield MockdomainDomain()

    @staticmethod
    @pytest.fixture()
    def problem(domain: AbstractDomain):
        yield domain.get_problem("1")

    @staticmethod
    @pytest.fixture()
    def solve_config():
        yield SolveConfig(
            jobs=1,
            memout=4 * 1024 * 1024 * 1024,  # 4GB
            timeout=350,
            timeout_offset=0,
            db_only=False,
            no_db_load=False,
            no_db_save=True,
        )

    # ============================================================================ #
    #                                     Tests                                    #
    # ============================================================================ #

    # =================================== Names ================================== #

    @pytest.mark.parametrize("name", ["name1", "name2"])
    def test_general_name(self, name: str):
        config = replace(self.config(), name=name)
        planner = Planner(config)
        assert planner.name == name

    @pytest.mark.parametrize("name", ["name1", "name2"])
    def test_oneshot_name(self, name: str):
        config = replace(self.config(), oneshot_name=name)
        planner = Planner(config)
        assert planner.oneshot_name == name

    @pytest.mark.parametrize("name", ["name1", "name2"])
    def test_oneshot_name_default(self, name: str):
        config = replace(self.config(), name=name, oneshot_name=None)
        planner = Planner(config)
        assert planner.oneshot_name == name

    @pytest.mark.parametrize("name", ["name1", "name2"])
    def test_anytime_name(self, name: str):
        config = replace(self.config(), anytime_name=name)
        planner = Planner(config)
        assert planner.anytime_name == name

    @pytest.mark.parametrize("name", ["name1", "name2"])
    def test_anytime_name_default(self, name: str):
        config = replace(self.config(), name=name, anytime_name=None)
        planner = Planner(config)
        assert planner.anytime_name == name

    # =============================== Get log file =============================== #

    @pytest.mark.parametrize("problem_id", ["1", "6"])
    @pytest.mark.parametrize("domain_name", ["domain1", "domain2"])
    @pytest.mark.parametrize("planner_name", ["planner1", "planner2"])
    @pytest.mark.parametrize("file_name", ["solve", "error", "warning"])
    @pytest.mark.parametrize("running_mode", RunningMode)
    def test_get_log_file(
        self,
        planner: Planner,
        problem: ProblemInstance,
        planner_name: str,
        domain_name: str,
        problem_id: str,
        file_name: str,
        running_mode: RunningMode,
    ):
        old_config = planner.config
        old_uid = problem.uid
        old_name = problem.domain.name

        planner._config = replace(planner.config, name=planner_name)
        problem._uid = problem_id
        problem.domain._name = domain_name

        expected = (
            TyrPaths().logs
            / planner_name
            / domain_name
            / f"{problem_id}-{running_mode.name.lower()}"
            / f"{file_name}.log"
        )
        result = planner.get_log_file(problem, file_name, running_mode)
        assert result == expected

        planner._config = old_config
        problem._uid = old_uid
        problem.domain._name = old_name

    # ================================ Get version =============================== #

    def test_get_correct_version(self, planner: Planner, problem: ProblemInstance):
        name, version = planner.get_version(problem)
        assert name == "base"
        assert version.uid == problem.uid * 3

    def test_get_inexistant_version(self, planner: Planner, problem: ProblemInstance):
        planner.config.problems["mockdomain"] = "inexistant"
        name, version = planner.get_version(problem)
        assert name is None
        assert version is None

    def test_get_version_from_unsupported_domain(
        self, planner: Planner, problem: ProblemInstance
    ):
        planner.config.problems.clear()
        name, version = planner.get_version(problem)
        assert name == "base"
        assert version.uid == problem.uid * 3

    # ================================= Database ================================= #

    def test_solver_database_result(
        self,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        db = Database()
        with patch.object(db, "load_planner_result") as load_mock:
            result = list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
            assert result == load_mock.return_value

    def test_solver_database_result_no_db_load(
        self,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        solve_config = replace(solve_config, no_db_load=True)
        db = Database()
        with patch.object(db, "load_planner_result") as load_mock:
            list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
            load_mock.assert_not_called()

    def test_solver_database_result_db_only(
        self,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        solve_config = replace(solve_config, db_only=True)
        db = Database()
        with patch.object(db, "load_planner_result") as load_mock:
            result = list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
            assert result == load_mock.return_value

    def test_solver_database_result_db_only_not_found(
        self,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        solve_config = replace(solve_config, db_only=True)
        db = Database()
        with patch.object(db, "load_planner_result") as load_mock:
            load_mock.return_value = None
            result = list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
            assert result.status == PlannerResultStatus.NOT_RUN

    def test_solver_database_save_result(
        self,
        mock_planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        solve_config = replace(solve_config, no_db_save=False)
        db = Database()
        with patch.object(db, "save_planner_result") as save_mock:
            result = PlannerResult(
                mock_planner.name,
                problem,
                RunningMode.ONESHOT,
                PlannerResultStatus.SOLVED,
                solve_config,
            )
            mock_planner._solve.return_value = [result]
            mock_planner.solve = lambda x, y, z: list(
                Planner.solve(mock_planner, x, y, z)
            )
            mock_planner.solve(problem, solve_config, RunningMode.ONESHOT)
            save_mock.assert_called_once_with(result)

    def test_solver_database_save_result_no_db_save(
        self,
        mock_planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        solve_config = replace(solve_config, no_db_save=True)
        db = Database()
        with patch.object(db, "save_planner_result") as save_mock:
            result = PlannerResult(
                mock_planner.name,
                problem,
                RunningMode.ONESHOT,
                PlannerResultStatus.SOLVED,
                solve_config,
            )
            mock_planner._solve.return_value = [result]
            mock_planner.solve = lambda x, y, z: list(
                Planner.solve(mock_planner, x, y, z)
            )
            mock_planner.solve(problem, solve_config, RunningMode.ONESHOT)
            save_mock.assert_not_called()

    @pytest.mark.parametrize("running_mode", RunningMode)
    def test_solver_database_save_result_not_duplicate_first_as_oneshot(
        self,
        mock_planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
        running_mode: RunningMode,
    ):
        solve_config = replace(solve_config, no_db_save=False)
        db = Database()
        with patch.object(db, "save_planner_result") as save_mock:
            result1 = PlannerResult(
                mock_planner.name,
                problem,
                running_mode,
                PlannerResultStatus.SOLVED,
                solve_config,
            )
            result2 = PlannerResult(
                mock_planner.name,
                problem,
                running_mode,
                PlannerResultStatus.ERROR,
                solve_config,
            )
            mock_planner._solve.return_value = [result1, result2]
            mock_planner.solve = lambda x, y, z: list(
                Planner.solve(mock_planner, x, y, z)
            )
            mock_planner.solve(problem, solve_config, running_mode)
            first_call = call(result1)
            final_call = call(result2)
            save_mock.assert_has_calls([first_call, final_call])
            assert save_mock.call_count == 2

    # =================================== Solve ================================== #

    @pytest.mark.parametrize(
        "running_mode",
        [
            pytest.param(
                r,
                marks=[pytest.mark.xfail] if r == RunningMode.MERGED else [],
            )
            for r in RunningMode
        ],
    )
    def test_solve_get_version_if_db_has_nothing(
        self,
        mock_planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
        running_mode: RunningMode,
    ):
        solve_config = replace(solve_config, no_db_load=True)
        mock_planner.solve = lambda x, y, z: list(Planner.solve(mock_planner, x, y, z))
        mock_planner._solve = lambda x, y, z: Planner._solve(mock_planner, x, y, z)
        try:
            mock_planner.solve(problem, solve_config, running_mode)
        except Exception:  # nosec: B110
            print(traceback.format_exc())
        mock_planner.get_version.assert_called_once_with(problem)

    def test_solve_no_available_version(
        self,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        planner.config.problems["foo"] = "bar"
        problem.domain._name = "foo"
        expected = PlannerResult.unsupported(
            problem,
            planner,
            solve_config,
            RunningMode.ONESHOT,
        )
        result = list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
        assert result == expected

    @pytest.mark.parametrize("timeout", [1, 15, 6])
    @patch("unified_planning.shortcuts.OneshotPlanner", autospec=True)
    def test_solve_using_upf_oneshot(
        self,
        mocked_oneshot_planner: Mock,
        timeout: int,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        solve_config = replace(solve_config, timeout=timeout)
        mocked_planner = mocked_oneshot_planner.return_value.__enter__.return_value
        _, version = planner.get_version(problem)

        try:
            res = list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
        except Exception:  # nosec: B110
            pass

        assert res.planner_name == planner.name
        mocked_oneshot_planner.assert_called_once_with(name=planner.oneshot_name)
        mocked_planner.solve.assert_called_once()
        solve_args, solve_kwargs = mocked_planner.solve.call_args
        assert solve_args == (version,)
        assert len(solve_kwargs) == 2
        assert solve_kwargs["timeout"] == timeout
        assert (
            solve_kwargs["output_stream"].name
            == planner.get_log_file(problem, "solve", RunningMode.ONESHOT).as_posix()
        )

    @pytest.mark.parametrize("timeout", [1, 15, 6])
    @patch("unified_planning.shortcuts.AnytimePlanner", autospec=True)
    def test_solve_using_upf_anytime(
        self,
        mocked_anytime_planner: Mock,
        timeout: int,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        solve_config = replace(solve_config, timeout=timeout)
        mocked_planner = mocked_anytime_planner.return_value.__enter__.return_value
        _, version = planner.get_version(problem)

        try:
            res = list(planner.solve(problem, solve_config, RunningMode.ANYTIME))
        except Exception:  # nosec: B110
            pass

        assert all(r.planner_name == planner.name for r in res)
        mocked_anytime_planner.assert_called_once_with(name=planner.anytime_name)
        mocked_planner.get_solutions.assert_called_once()
        solve_args, solve_kwargs = mocked_planner.get_solutions.call_args
        assert solve_args == (version,)
        assert len(solve_kwargs) == 2
        assert solve_kwargs["timeout"] == timeout
        assert (
            solve_kwargs["output_stream"].name
            == planner.get_log_file(problem, "solve", RunningMode.ANYTIME).as_posix()
        )

    @patch("unified_planning.shortcuts.OneshotPlanner", autospec=True)
    @patch("tyr.planners.model.planner.PlannerResult.from_upf", autospec=True)
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

        result = list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
        mocked_result_from_upf.assert_called_once_with(
            planner.name,
            problem,
            "base",
            upf_result,
            solve_config,
            RunningMode.ONESHOT,
        )
        assert result == mocked_result_from_upf.return_value

    @pytest.mark.parametrize("computation_time", [1, 10, 15.7])
    @patch("unified_planning.shortcuts.OneshotPlanner", autospec=True)
    @patch("traceback.format_exc")
    def test_solve_error(
        self,
        mocked_traceback: Mock,
        mocked_oneshot_planner: Mock,
        computation_time: float,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        mocked_traceback.return_value = "foo toto"
        mocked_planner = mocked_oneshot_planner.return_value.__enter__.return_value
        mocked_planner.solve.side_effect = RuntimeError("foo toto")
        expected = PlannerResult.error(
            problem,
            planner,
            solve_config,
            RunningMode.ONESHOT,
            computation_time,
            "foo toto",
        )
        with patch("time.time", side_effect=[0, 0, 0, computation_time]):
            result = list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
        assert result == expected

    @patch("builtins.open")
    @patch("unified_planning.shortcuts.OneshotPlanner", autospec=True)
    def test_solve_error_write_in_logs(
        self,
        mocked_oneshot_planner: Mock,
        mocked_open: Mock,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        mocked_planner = mocked_oneshot_planner.return_value.__enter__.return_value
        mocked_planner.solve.side_effect = RuntimeError
        log_path = planner.get_log_file(problem, "error", RunningMode.ONESHOT)
        list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
        mocked_open.assert_called_with(log_path, "w", encoding="utf-8")

    @pytest.mark.parametrize("computation_time", [1, 10, 15.7])
    @patch("unified_planning.shortcuts.OneshotPlanner", autospec=True)
    @patch("tyr.planners.model.planner.PlannerResult.from_upf", autospec=True)
    def test_solve_computation_time(
        self,
        mocked_result_from_upf: Mock,
        mocked_oneshot_planner: Mock,
        computation_time: float,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        upf_result = PlannerResult(
            planner.name,
            problem,
            RunningMode.ONESHOT,
            PlannerResultStatus.SOLVED,
            solve_config,
        )
        mocked_result_from_upf.return_value = upf_result
        expected = replace(upf_result, computation_time=computation_time)
        with patch("time.time", side_effect=[0, 0, 0, computation_time]):
            result = list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
        assert result == expected

    @pytest.mark.slow
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
        solve_config = replace(solve_config, timeout=timeout)

        expected = PlannerResult.timeout(
            problem,
            planner,
            solve_config,
            RunningMode.ONESHOT,
        )
        result = list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
        assert result == expected

    @pytest.mark.slow
    @pytest.mark.timeout(3)
    @pytest.mark.parametrize("timeout", [1, 2])
    @patch("unified_planning.shortcuts.OneshotPlanner", autospec=True)
    def test_solve_timeout_kill_running_process(
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
        mocked_kill: Mock = mocked_planner._process.kill
        solve_config = replace(solve_config, timeout=timeout)

        list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
        mocked_kill.assert_called_once()

    @pytest.mark.slow
    @pytest.mark.timeout(3)
    @pytest.mark.parametrize("timeout", [1, 2])
    @patch("unified_planning.shortcuts.OneshotPlanner", autospec=True)
    def test_solve_timeout_do_not_crash_if_process_already_killed(
        self,
        mocked_oneshot_planner: Mock,
        timeout: int,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        def error(*args, **kwargs):
            raise OSError("Process already killed")

        def solve(*args, **kwargs):
            time.sleep(timeout + 10)

        solve_config = replace(solve_config, timeout=timeout)
        mocked_planner = mocked_oneshot_planner.return_value.__enter__.return_value
        mocked_planner.solve.side_effect = solve
        mocked_kill: Mock = mocked_planner._process.kill
        mocked_kill.side_effect = error
        solve_config = replace(solve_config, timeout=timeout)

        result = list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
        assert result.status == PlannerResultStatus.TIMEOUT
        mocked_kill.assert_called_once()

    @pytest.mark.skip(reason="Disabled feature")
    @pytest.mark.parametrize("timeout", [10, 200])
    @patch("unified_planning.shortcuts.OneshotPlanner", autospec=True)
    @patch("tyr.planners.model.planner.PlannerResult.from_upf", autospec=True)
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
            RunningMode.ONESHOT,
            PlannerResultStatus.SOLVED,
            solve_config,
            computation_time=2 * timeout,
        )
        mocked_result_from_upf.return_value = upf_result
        solve_config = replace(solve_config, timeout=timeout)

        expected = PlannerResult.timeout(
            problem, planner, solve_config, RunningMode.ONESHOT
        )
        result = list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
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
        list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
        mock_resource.assert_called_once_with(
            resource.RLIMIT_AS, (memout, resource.RLIM_INFINITY)
        )

    @patch("unified_planning.shortcuts.OneshotPlanner", autospec=True)
    def test_solve_skip_checks(
        self,
        mocked_oneshot_planner: Mock,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        mocked_planner = mocked_oneshot_planner.return_value.__enter__.return_value
        list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
        assert mocked_planner.skip_checks is True

    @patch.dict(os.environ, {"MY_VARIABLE": "initial_value", "MY_BOOL": "False"})
    def test_solve_set_env_params(
        self,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        assert os.environ["MY_VARIABLE"] == "initial_value"
        assert os.environ["MY_BOOL"] == "False"
        list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
        assert os.environ["MY_VARIABLE"] == "new_value"
        assert os.environ["MY_BOOL"] == "True"

    @patch("shutil.rmtree")
    def test_solve_clear_logs(
        self,
        mocked_rmtree: Mock,
        planner: Planner,
        problem: ProblemInstance,
        solve_config: SolveConfig,
    ):
        log_folder = planner.get_log_file(problem, "", RunningMode.ONESHOT).parent
        list(planner.solve(problem, solve_config, RunningMode.ONESHOT))[-1]
        mocked_rmtree.assert_called_once_with(log_folder, True)

    def test_solve_single(
        self, mock_planner: Planner, problem: ProblemInstance, solve_config: SolveConfig
    ):
        mock_planner._solve.return_value = list([Mock(), Mock(), Mock()])
        mock_planner.solve = lambda x, y, z: iter(Planner.solve(mock_planner, x, y, z))
        mock_planner.solve_single = lambda x, y, z: Planner.solve_single(
            mock_planner, x, y, z
        )

        result = mock_planner.solve_single(problem, solve_config, RunningMode.ONESHOT)
        assert result == mock_planner._solve.return_value[-1]

    # ================================= Equality ================================= #

    def test_eq(self):
        config1 = PlannerConfig(name="planner1", problems={"domain1": "version1"})
        config2 = PlannerConfig(name="planner1", problems={"domain1": "version1"})
        planner1 = Planner(config1)
        planner2 = Planner(config2)
        assert planner1 == planner2

    def test_neq(self):
        config1 = PlannerConfig(name="planner1", problems={"domain1": "version1"})
        config2 = PlannerConfig(name="planner2", problems={"domain2": "version2"})
        planner1 = Planner(config1)
        planner2 = Planner(config2)
        assert planner1 != planner2

    def test_eq_non_planner(self):
        config1 = PlannerConfig(name="planner1", problems={"domain1": "version1"})
        config2 = PlannerConfig(name="planner1", problems={"domain1": "version1"})
        planner1 = Planner(config1)
        planner2 = {"config": config2}
        assert planner1 != planner2

    def test_hash(self):
        config = PlannerConfig(name="planner1", problems={"domain1": "version1"})
        planner = Planner(config)
        expected = hash(config)
        result = hash(planner)
        assert result == expected
