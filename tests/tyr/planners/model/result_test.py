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
