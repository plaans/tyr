from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional

from unified_planning.engines.results import (
    PlanGenerationResult,
    PlanGenerationResultStatus,
)

from tyr.problem import ProblemInstance

if TYPE_CHECKING:
    from tyr.planner.model.planner import Planner


class PlannerResultStatus(Enum):
    """Represents the possible status of a planner result."""

    SOLVED = auto()
    UNSOLVABLE = auto()
    TIMEOUT = auto()
    MEMOUT = auto()
    ERROR = auto()
    UNSUPPORTED = auto()

    @staticmethod
    def from_upf(status: PlanGenerationResultStatus) -> "PlannerResultStatus":
        """Converts a status from the unified planning library to our status format.

        Args:
            status (PlanGenerationResultStatus): The status to convert.

        Returns:
            PlannerResultStatus: The inner matching status.
        """
        return {
            PlanGenerationResultStatus.SOLVED_OPTIMALLY: PlannerResultStatus.SOLVED,
            PlanGenerationResultStatus.SOLVED_SATISFICING: PlannerResultStatus.SOLVED,
            PlanGenerationResultStatus.UNSOLVABLE_PROVEN: PlannerResultStatus.UNSOLVABLE,
            PlanGenerationResultStatus.UNSOLVABLE_INCOMPLETELY: PlannerResultStatus.UNSOLVABLE,
            PlanGenerationResultStatus.TIMEOUT: PlannerResultStatus.TIMEOUT,
            PlanGenerationResultStatus.MEMOUT: PlannerResultStatus.MEMOUT,
            PlanGenerationResultStatus.INTERNAL_ERROR: PlannerResultStatus.ERROR,
            PlanGenerationResultStatus.UNSUPPORTED_PROBLEM: PlannerResultStatus.UNSUPPORTED,
            PlanGenerationResultStatus.INTERMEDIATE: PlannerResultStatus.SOLVED,
        }[status]


@dataclass
class PlannerResult:
    """Represents the result of a planner solving a problem."""

    planner_name: str
    problem: ProblemInstance
    status: PlannerResultStatus
    computation_time: Optional[float]
    plan: Optional[str]
    plan_quality: Optional[float]

    @staticmethod
    def from_upf(
        problem: ProblemInstance,
        result: PlanGenerationResult,
    ) -> "PlannerResult":
        """Converts a result from the unified planning library to our inner result format.

        Args:
            problem (ProblemInstance): The problem solved by the planner.
            result (PlanGenerationResult): The result to convert.

        Returns:
            PlannerResult: The inner matching result.
        """
        computation_key = "engine_internal_time"
        computation_time = None
        if result.metrics is not None and computation_key in result.metrics:
            computation_time = float(result.metrics[computation_key])

        plan, plan_quality = None, None
        if result.plan is not None:
            plan = str(result.plan)
            plan_quality = problem.get_quality_of_plan(plan)

        return PlannerResult(
            result.engine_name,
            problem,
            PlannerResultStatus.from_upf(result.status),
            computation_time,
            plan,
            plan_quality,
        )

    @staticmethod
    def unsupported(problem: ProblemInstance, planner: "Planner") -> "PlannerResult":
        """Creates an unsupported result.

        Args:
            problem (ProblemInstance): The unsupported problem.
            planner (Planner): The planner trying the solve the problem.

        Returns:
            PlannerResult: The unsupported result.
        """
        return PlannerResult(
            planner.name,
            problem,
            PlannerResultStatus.UNSUPPORTED,
            computation_time=None,
            plan=None,
            plan_quality=None,
        )

    @staticmethod
    def error(
        problem: ProblemInstance, planner: "Planner", computation_time: float
    ) -> "PlannerResult":
        """Creates an error result.

        Args:
            problem (ProblemInstance): The erroneous problem.
            planner (Planner): The planner trying the solve the problem.
            computation_time (float): Time to reach the error.

        Returns:
            PlannerResult: The error result.
        """
        return PlannerResult(
            planner.name,
            problem,
            PlannerResultStatus.ERROR,
            computation_time,
            plan=None,
            plan_quality=None,
        )
