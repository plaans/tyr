import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional

from unified_planning.engines.results import (
    PlanGenerationResult,
    PlanGenerationResultStatus,
)
from unified_planning.plans import Plan

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
    computation_time: Optional[float] = None
    plan: Optional[str] = None
    plan_quality: Optional[float] = None

    @staticmethod
    def _convert_upf_plan(upf_plan: Plan) -> str:
        plan = []

        for line in str(upf_plan).split("\n"):
            if line.strip() != "":
                action_match = re.match(r"^\s*(\w+)(?:\(([^)]+)\))?\s*$", line)
                if action_match:
                    action_name = action_match.group(1)
                    parameters = action_match.group(2)
                    if parameters is not None:
                        parameters = " " + parameters.replace(",", "")
                    else:
                        parameters = ""
                    action = f"({action_name}{parameters})"
                    plan.append(action)

        return "\n".join(plan)

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
            plan = PlannerResult._convert_upf_plan(result.plan)
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

    @staticmethod
    def timeout(
        problem: ProblemInstance, planner: "Planner", timeout: int
    ) -> "PlannerResult":
        """Creates a timeout result.

        Args:
            problem (ProblemInstance): The timed out problem.
            planner (Planner): The planner trying the solve the problem.
            timeout (int): The limit time to solve the problem.

        Returns:
            PlannerResult: The timeout result.
        """
        return PlannerResult(
            planner.name,
            problem,
            PlannerResultStatus.TIMEOUT,
            timeout,
            plan=None,
            plan_quality=None,
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
