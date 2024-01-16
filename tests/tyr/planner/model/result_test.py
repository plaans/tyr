from typing import Optional
from unittest.mock import MagicMock, Mock

import pytest
from unified_planning.engines.results import (
    PlanGenerationResult,
    PlanGenerationResultStatus,
)

from tyr import PlannerResult, PlannerResultStatus


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
    def test_from_upf_problem(self, problem: Mock, upf_result: PlanGenerationResult):
        result = PlannerResult.from_upf(problem, upf_result)
        assert result.problem == problem

    @pytest.mark.parametrize("status", PlanGenerationResultStatus)
    def test_from_upf_status(
        self,
        status: PlanGenerationResultStatus,
        problem: Mock,
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
        result = PlannerResult.from_upf(problem, upf_result)
        assert result.status == status_map[status]

    @pytest.mark.parametrize("name", ["mockplanner", "mockplannerbis"])
    def test_from_upf_planner_name(
        self, name: str, problem: Mock, upf_result: PlanGenerationResult
    ):
        upf_result.engine_name = name
        result = PlannerResult.from_upf(problem, upf_result)
        assert result.planner_name == name

    @pytest.mark.parametrize("computation_time", [None, "1.5", "0.0", "15"])
    def test_from_upf_computation_time(
        self,
        computation_time: Optional[str],
        problem: Mock,
        upf_result: PlanGenerationResult,
    ):
        if computation_time is None:
            upf_result.metrics = None
            expected = None
        else:
            upf_result.metrics = {"engine_internal_time": computation_time}
            expected = float(computation_time)
        result = PlannerResult.from_upf(problem, upf_result)
        assert result.computation_time == expected

    @pytest.mark.parametrize("plan", [None, MagicMock(), MagicMock()])
    def test_from_upf_plan(
        self,
        plan: Optional[Mock],
        problem: Mock,
        upf_result: PlanGenerationResult,
    ):
        upf_result.plan = plan
        expected = None if plan is None else str(plan)
        result = PlannerResult.from_upf(problem, upf_result)
        assert result.plan == expected

    @pytest.mark.parametrize(
        ["plan", "quality"], [(None, None), (MagicMock(), 15), (MagicMock(), 7.6)]
    )
    def test_from_upf_plan_quality(
        self,
        plan: Optional[Mock],
        quality: Optional[float],
        problem: Mock,
        upf_result: PlanGenerationResult,
    ):
        upf_result.plan = plan
        problem.get_quality_of_plan.return_value = quality
        result = PlannerResult.from_upf(problem, upf_result)

        assert result.plan_quality == quality
        if plan is None:
            problem.get_quality_of_plan.assert_not_called()
        else:
            problem.get_quality_of_plan.assert_called_once_with(str(plan))

    # ================================ Unsupported =============================== #

    @pytest.mark.parametrize("name", ["mockplanner", "mockplannerbis"])
    @pytest.mark.parametrize("problem", [MagicMock(), MagicMock()])
    def test_unsupported(self, name: str, problem: Mock):
        planner = MagicMock()
        planner.name = name
        expected = PlannerResult(
            name,
            problem,
            PlannerResultStatus.UNSUPPORTED,
            computation_time=None,
            plan=None,
            plan_quality=None,
        )
        result = PlannerResult.unsupported(problem, planner)
        assert result == expected

    # =================================== Error ================================== #

    @pytest.mark.parametrize("name", ["mockplanner", "mockplannerbis"])
    @pytest.mark.parametrize("problem", [MagicMock(), MagicMock()])
    @pytest.mark.parametrize("computation_time", [1.5, 0, 16])
    def test_error(self, name: str, problem: Mock, computation_time: float):
        planner = MagicMock()
        planner.name = name
        expected = PlannerResult(
            name,
            problem,
            PlannerResultStatus.ERROR,
            computation_time,
            plan=None,
            plan_quality=None,
        )
        result = PlannerResult.error(problem, planner, computation_time)
        assert result == expected
