from dataclasses import replace
from typing import Optional
from unittest.mock import MagicMock, Mock

import pytest
from unified_planning.engines.results import (
    PlanGenerationResult,
    PlanGenerationResultStatus,
)

from tyr import PlannerResult, PlannerResultStatus, RunningMode


class TestPlannerResult:
    # ============================================================================ #
    #                                    Getters                                   #
    # ============================================================================ #

    @staticmethod
    @pytest.fixture()
    def problem():
        yield MagicMock()

    @staticmethod
    @pytest.fixture()
    def config():
        yield MagicMock()

    @staticmethod
    @pytest.fixture()
    def upf_result():
        yield PlanGenerationResult(
            PlanGenerationResultStatus.SOLVED_OPTIMALLY,
            plan=None,
            engine_name="mockplanner",
        )

    # ============================================================================ #
    #                                     Tests                                    #
    # ============================================================================ #

    # ================================= From UPF ================================= #

    @pytest.mark.parametrize("problem", [MagicMock(), MagicMock()])
    def test_from_upf_problem(
        self,
        problem: Mock,
        config: Mock,
        upf_result: PlanGenerationResult,
    ):
        result = PlannerResult.from_upf(
            "mockplanner",
            problem,
            "version_name",
            upf_result,
            config,
            RunningMode.ONESHOT,
        )
        assert result.problem == problem

    @pytest.mark.parametrize("status", PlanGenerationResultStatus)
    def test_from_upf_status(
        self,
        status: PlanGenerationResultStatus,
        problem: Mock,
        config: Mock,
        upf_result: PlanGenerationResult,
    ):
        status_map = {
            PlanGenerationResultStatus.SOLVED_OPTIMALLY: PlannerResultStatus.SOLVED,
            PlanGenerationResultStatus.SOLVED_SATISFICING: PlannerResultStatus.SOLVED,
            PlanGenerationResultStatus.UNSOLVABLE_PROVEN: PlannerResultStatus.UNSOLVABLE,
            PlanGenerationResultStatus.UNSOLVABLE_INCOMPLETELY: PlannerResultStatus.UNSOLVABLE,
            PlanGenerationResultStatus.TIMEOUT: PlannerResultStatus.TIMEOUT,
            PlanGenerationResultStatus.MEMOUT: PlannerResultStatus.MEMOUT,
            PlanGenerationResultStatus.INTERNAL_ERROR: PlannerResultStatus.ERROR,
            PlanGenerationResultStatus.UNSUPPORTED_PROBLEM: PlannerResultStatus.UNSUPPORTED,
            PlanGenerationResultStatus.INTERMEDIATE: PlannerResultStatus.SOLVED,
        }
        upf_result.status = status
        result = PlannerResult.from_upf(
            "mockplanner",
            problem,
            "version_name",
            upf_result,
            config,
            RunningMode.ONESHOT,
        )
        assert result.status == status_map[status]

    @pytest.mark.parametrize("name", ["mockplanner", "mockplannerbis"])
    def test_from_upf_planner_name(
        self,
        name: str,
        problem: Mock,
        config: Mock,
        upf_result: PlanGenerationResult,
    ):
        result = PlannerResult.from_upf(
            name,
            problem,
            "version_name",
            upf_result,
            config,
            RunningMode.ONESHOT,
        )
        assert result.planner_name == name

    @pytest.mark.parametrize("computation_time", [None, "1.5", "0.0", "15"])
    def test_from_upf_computation_time(
        self,
        computation_time: Optional[str],
        problem: Mock,
        config: Mock,
        upf_result: PlanGenerationResult,
    ):
        if computation_time is None:
            upf_result.metrics = None
            expected = None
        else:
            upf_result.metrics = {"engine_internal_time": computation_time}
            expected = float(computation_time)
        result = PlannerResult.from_upf(
            "mockplanner",
            problem,
            "version_name",
            upf_result,
            config,
            RunningMode.ONESHOT,
        )
        assert result.computation_time == expected

    @pytest.mark.parametrize(
        ["plan", "quality"], [(None, None), (MagicMock(), 15), (MagicMock(), 7.6)]
    )
    @pytest.mark.parametrize("version_name", [MagicMock(), MagicMock()])
    def test_from_upf_plan_quality(
        self,
        plan: Optional[Mock],
        quality: Optional[float],
        version_name: str,
        problem: Mock,
        config: Mock,
        upf_result: PlanGenerationResult,
    ):
        upf_result.plan = plan
        problem.get_quality_of_plan.return_value = quality
        result = PlannerResult.from_upf(
            "mockplanner",
            problem,
            version_name,
            upf_result,
            config,
            RunningMode.ONESHOT,
        )

        assert result.plan_quality == quality
        if plan is None:
            problem.get_quality_of_plan.assert_not_called()
        else:
            problem.get_quality_of_plan.assert_called_once_with(plan, version_name)

    # =================================== Merge ================================== #

    def test_merge_same_results(self):
        result1 = PlannerResult(
            config="config",
            planner_name="planner",
            problem="problem",
            computation_time=10.0,
            plan_quality=0.5,
            status=PlannerResultStatus.SOLVED,
            running_mode=RunningMode.ONESHOT,
        )
        result2 = PlannerResult(
            config="config",
            planner_name="planner",
            problem="problem",
            computation_time=5.0,
            plan_quality=0.8,
            status=PlannerResultStatus.SOLVED,
            running_mode=RunningMode.ONESHOT,
        )
        merged_result = result1.merge(result2)
        assert merged_result.config == "config"
        assert merged_result.planner_name == "planner"
        assert merged_result.problem == "problem"
        assert merged_result.computation_time == 5.0
        assert merged_result.plan_quality == 0.5
        assert merged_result.status == PlannerResultStatus.SOLVED

    def test_merge_different_config(self):
        result1 = PlannerResult(
            config="config1",
            planner_name="planner",
            problem="problem",
            computation_time=10.0,
            plan_quality=0.9,
            status=PlannerResultStatus.SOLVED,
            running_mode=RunningMode.ONESHOT,
        )
        result2 = PlannerResult(
            config="config2",
            planner_name="planner",
            problem="problem",
            computation_time=5.0,
            plan_quality=0.8,
            status=PlannerResultStatus.SOLVED,
            running_mode=RunningMode.ONESHOT,
        )
        with pytest.raises(ValueError):
            result1.merge(result2)

    def test_merge_different_planners(self):
        result1 = PlannerResult(
            config="config",
            planner_name="planner1",
            problem="problem",
            computation_time=10.0,
            plan_quality=0.9,
            status=PlannerResultStatus.SOLVED,
            running_mode=RunningMode.ONESHOT,
        )
        result2 = PlannerResult(
            config="config",
            planner_name="planner2",
            problem="problem",
            computation_time=5.0,
            plan_quality=0.8,
            status=PlannerResultStatus.SOLVED,
            running_mode=RunningMode.ONESHOT,
        )
        with pytest.raises(ValueError):
            result1.merge(result2)

    def test_merge_different_problems(self):
        result1 = PlannerResult(
            config="config",
            planner_name="planner",
            problem="problem1",
            computation_time=10.0,
            plan_quality=0.9,
            status=PlannerResultStatus.SOLVED,
            running_mode=RunningMode.ONESHOT,
        )
        result2 = PlannerResult(
            config="config",
            planner_name="planner",
            problem="problem2",
            computation_time=5.0,
            plan_quality=0.8,
            status=PlannerResultStatus.SOLVED,
            running_mode=RunningMode.ONESHOT,
        )
        with pytest.raises(ValueError):
            result1.merge(result2)

    def test_merge_other_result_not_solved(self):
        result1 = PlannerResult(
            config="config",
            planner_name="planner",
            problem="problem",
            computation_time=10.0,
            plan_quality=0.9,
            status=PlannerResultStatus.SOLVED,
            running_mode=RunningMode.ONESHOT,
        )
        result2 = PlannerResult(
            config="config",
            planner_name="planner",
            problem="problem",
            computation_time=None,
            plan_quality=None,
            status=PlannerResultStatus.TIMEOUT,
            running_mode=RunningMode.ONESHOT,
        )
        merged_result = result1.merge(result2)
        assert merged_result == replace(result1, running_mode=RunningMode.MERGED)

    def test_merge_self_result_not_solved(self):
        result1 = PlannerResult(
            config="config",
            planner_name="planner",
            problem="problem",
            computation_time=None,
            plan_quality=None,
            status=PlannerResultStatus.TIMEOUT,
            running_mode=RunningMode.ONESHOT,
        )
        result2 = PlannerResult(
            config="config",
            planner_name="planner",
            problem="problem",
            computation_time=10.0,
            plan_quality=0.9,
            status=PlannerResultStatus.SOLVED,
            running_mode=RunningMode.ONESHOT,
        )
        merged_result = result1.merge(result2)
        assert merged_result == replace(result2, running_mode=RunningMode.MERGED)

    def test_merge_all(self):
        result1 = PlannerResult(
            config="config",
            planner_name="planner",
            problem="problem",
            computation_time=10.0,
            plan_quality=0.5,
            status=PlannerResultStatus.SOLVED,
            running_mode=RunningMode.ONESHOT,
        )
        result2 = PlannerResult(
            config="config",
            planner_name="planner",
            problem="problem",
            computation_time=5.0,
            plan_quality=0.8,
            status=PlannerResultStatus.SOLVED,
            running_mode=RunningMode.ONESHOT,
        )
        result3 = PlannerResult(
            config="config",
            planner_name="planner-bis",
            problem="problem",
            computation_time=5.0,
            plan_quality=0.8,
            status=PlannerResultStatus.SOLVED,
            running_mode=RunningMode.ONESHOT,
        )
        result4 = PlannerResult(
            config="config",
            planner_name="planner-bis",
            problem="problem-bis",
            computation_time=5.0,
            plan_quality=0.8,
            status=PlannerResultStatus.SOLVED,
            running_mode=RunningMode.ONESHOT,
        )
        results = [result1, result2, result3, result4]

        expected = [result1.merge(result2), result3, result4]
        merged_results = PlannerResult.merge_all(results)
        assert merged_results == expected

    # =================================== Error ================================== #

    @pytest.mark.parametrize("name", ["mockplanner", "mockplannerbis"])
    @pytest.mark.parametrize("problem", [MagicMock(), MagicMock()])
    @pytest.mark.parametrize("computation_time", [1.5, 0, 16])
    @pytest.mark.parametrize("message", ["foo", "bar"])
    def test_error(
        self,
        name: str,
        problem: Mock,
        config: Mock,
        computation_time: float,
        message: str,
    ):
        planner = MagicMock()
        planner.name = name
        expected = PlannerResult(
            name,
            problem,
            RunningMode.ONESHOT,
            PlannerResultStatus.ERROR,
            config,
            computation_time,
            plan_quality=None,
            error_message=message,
        )
        result = PlannerResult.error(
            problem,
            planner,
            config,
            RunningMode.ONESHOT,
            computation_time,
            message,
        )
        assert result == expected

    # ================================== Not Run ================================= #

    @pytest.mark.parametrize("name", ["mockplanner", "mockplannerbis"])
    @pytest.mark.parametrize("problem", [MagicMock(), MagicMock()])
    def test_not_run(
        self,
        name: str,
        problem: Mock,
        config: Mock,
    ):
        planner = MagicMock()
        planner.name = name
        expected = PlannerResult(
            name,
            problem,
            RunningMode.ONESHOT,
            PlannerResultStatus.NOT_RUN,
            config,
            computation_time=None,
            plan_quality=None,
        )
        result = PlannerResult.not_run(problem, planner, config, RunningMode.ONESHOT)
        assert result == expected

    # ================================== Timeout ================================= #

    @pytest.mark.parametrize("name", ["mockplanner", "mockplannerbis"])
    @pytest.mark.parametrize("problem", [MagicMock(), MagicMock()])
    @pytest.mark.parametrize("timeout", [1, 0, 16])
    def test_timeout(self, name: str, problem: Mock, config: Mock, timeout: float):
        planner = MagicMock()
        planner.name = name
        config.timeout = timeout
        expected = PlannerResult(
            str(planner),
            problem,
            RunningMode.ONESHOT,
            PlannerResultStatus.TIMEOUT,
            config,
            timeout,
        )
        result = PlannerResult.timeout(problem, planner, config, RunningMode.ONESHOT)
        assert result == expected

    # ================================ Unsupported =============================== #

    @pytest.mark.parametrize("name", ["mockplanner", "mockplannerbis"])
    @pytest.mark.parametrize("problem", [MagicMock(), MagicMock()])
    def test_unsupported(self, name: str, problem: Mock, config: Mock):
        planner = MagicMock()
        planner.name = name
        expected = PlannerResult(
            name,
            problem,
            RunningMode.ONESHOT,
            PlannerResultStatus.UNSUPPORTED,
            config,
            computation_time=None,
            plan_quality=None,
        )
        result = PlannerResult.unsupported(
            problem,
            planner,
            config,
            RunningMode.ONESHOT,
        )
        assert result == expected
