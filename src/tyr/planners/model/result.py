from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional

from unified_planning.engines.results import (
    PlanGenerationResult,
    PlanGenerationResultStatus,
)

from tyr.planners.model.config import RunningMode
from tyr.problems import ProblemInstance

if TYPE_CHECKING:
    from tyr.planners.model.planner import Planner


class PlannerResultStatus(Enum):
    """Represents the possible status of a planner result."""

    SOLVED = auto()
    UNSOLVABLE = auto()
    TIMEOUT = auto()
    MEMOUT = auto()
    ERROR = auto()
    UNSUPPORTED = auto()
    NOT_RUN = auto()

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
class PlannerResult:  # pylint: disable = too-many-instance-attributes
    """Represents the result of a planner solving a problem."""

    planner_name: str
    problem: ProblemInstance
    running_mode: RunningMode
    status: PlannerResultStatus
    computation_time: Optional[float] = None
    plan_quality: Optional[float] = None
    error_message: str = ""
    from_database: bool = False

    @staticmethod
    def from_upf(
        problem: ProblemInstance,
        result: PlanGenerationResult,
        running_mode: RunningMode,
    ) -> "PlannerResult":
        """Converts a result from the unified planning library to our inner result format.

        Args:
            problem (ProblemInstance): The problem solved by the planner.
            result (PlanGenerationResult): The result to convert.
            running_mode (RunningMode): The mode used by the planner.

        Returns:
            PlannerResult: The inner matching result.
        """
        computation_key = "engine_internal_time"
        computation_time = None
        if result.metrics is not None and computation_key in result.metrics:
            computation_time = float(result.metrics[computation_key])

        plan_quality = None
        if result.plan is not None:
            plan_quality = problem.get_quality_of_plan(result.plan)

        return PlannerResult(
            result.engine_name,
            problem,
            running_mode,
            PlannerResultStatus.from_upf(result.status),
            computation_time,
            plan_quality,
        )

    @staticmethod
    def error(
        problem: ProblemInstance,
        planner: "Planner",
        running_mode: RunningMode,
        computation_time: float,
        message: str,
    ) -> "PlannerResult":
        """Creates an error result.

        Args:
            problem (ProblemInstance): The erroneous problem.
            planner (Planner): The planner trying the solve the problem.
            running_mode (RunningMode): The mode used by the planner.
            computation_time (float): Time to reach the error.

        Returns:
            PlannerResult: The error result.
        """
        return PlannerResult(
            planner.name,
            problem,
            running_mode,
            PlannerResultStatus.ERROR,
            computation_time,
            plan_quality=None,
            error_message=message,
        )

    @staticmethod
    def not_run(
        problem: ProblemInstance,
        planner: "Planner",
        running_mode: RunningMode,
    ) -> "PlannerResult":
        """Creates a not run result.

        Args:
            problem (ProblemInstance): The problem not run.
            planner (Planner): The planner trying the solve the problem.
            running_mode (RunningMode): The mode used by the planner.

        Returns:
            PlannerResult: The not run result.
        """
        return PlannerResult(
            planner.name,
            problem,
            running_mode,
            PlannerResultStatus.NOT_RUN,
            computation_time=None,
            plan_quality=None,
        )

    @staticmethod
    def timeout(
        problem: ProblemInstance,
        planner: "Planner",
        running_mode: RunningMode,
        timeout: int,
    ) -> "PlannerResult":
        """Creates a timeout result.

        Args:
            problem (ProblemInstance): The timed out problem.
            planner (Planner): The planner trying the solve the problem.
            running_mode (RunningMode): The mode used by the planner.
            timeout (int): The limit time to solve the problem.

        Returns:
            PlannerResult: The timeout result.
        """
        return PlannerResult(
            planner.name,
            problem,
            running_mode,
            PlannerResultStatus.TIMEOUT,
            timeout,
            plan_quality=None,
        )

    @staticmethod
    def unsupported(
        problem: ProblemInstance,
        planner: "Planner",
        running_mode: RunningMode,
    ) -> "PlannerResult":
        """Creates an unsupported result.

        Args:
            problem (ProblemInstance): The unsupported problem.
            planner (Planner): The planner trying the solve the problem.
            running_mode (RunningMode): The mode used by the planner.

        Returns:
            PlannerResult: The unsupported result.
        """
        return PlannerResult(
            planner.name,
            problem,
            running_mode,
            PlannerResultStatus.UNSUPPORTED,
            computation_time=None,
            plan_quality=None,
        )


__all__ = ["PlannerResult", "PlannerResultStatus"]
