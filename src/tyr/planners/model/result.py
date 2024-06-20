from dataclasses import dataclass, replace
from enum import Enum, auto
from typing import TYPE_CHECKING, List, Optional, Union

from unified_planning.engines.results import (
    PlanGenerationResult,
    PlanGenerationResultStatus,
)

from tyr.planners.model.config import RunningMode, SolveConfig
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
    config: SolveConfig
    computation_time: Optional[float] = None
    plan_quality: Optional[float] = None
    error_message: str = ""
    from_database: bool = False

    # pylint: disable = too-many-arguments
    @staticmethod
    def from_upf(
        planner_name: str,
        problem: ProblemInstance,
        version_name: str,
        result: PlanGenerationResult,
        config: SolveConfig,
        running_mode: RunningMode,
    ) -> "PlannerResult":
        """Converts a result from the unified planning library to our inner result format.

        Args:
            planner_name (str): The name of the planner solving the problem.
            problem (ProblemInstance): The problem solved by the planner.
            version_name (str): The name of the version of the problem solved.
            result (PlanGenerationResult): The result to convert.
            config (SolveConfig): The configuration used to solve the problem.
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
            plan_quality = problem.get_quality_of_plan(result.plan, version_name)

        return PlannerResult(
            planner_name,
            problem,
            running_mode,
            PlannerResultStatus.from_upf(result.status),
            config,
            computation_time,
            plan_quality,
        )

    def merge(self, other: "PlannerResult") -> "PlannerResult":
        """Merges two results into one.

        Args:
            other (PlannerResult): The other result to merge.

        Returns:
            PlannerResult: The merged result.
        """
        if self.config != other.config:
            raise ValueError("Cannot merge results with different configurations.")
        if self.planner_name != other.planner_name:
            raise ValueError("Cannot merge results from different planners.")
        if self.problem != other.problem:
            raise ValueError("Cannot merge results from different problems.")

        computation = min(
            (
                x.computation_time
                for x in (self, other)
                if x.computation_time is not None
            ),
            default=None,
        )
        quality = min(
            (x.plan_quality for x in (self, other) if x.plan_quality is not None),
            default=None,
        )

        args = {"running_mode": RunningMode.MERGED, "plan_quality": quality}
        if other.status != PlannerResultStatus.SOLVED:
            return replace(self, **args)  # type: ignore
        if self.status != PlannerResultStatus.SOLVED:
            return replace(other, **args)  # type: ignore
        return replace(self, computation_time=computation, **args)  # type: ignore

    @staticmethod
    def merge_all(results: List["PlannerResult"]) -> List["PlannerResult"]:
        """Merges a list of results into a list of merged results.

        Args:
            results (List[PlannerResult]): The results to merge.

        Returns:
                List[PlannerResult]: The merged results.
        """
        merged = {}
        for result in results:
            key = (result.problem, result.planner_name)
            if key not in merged:
                merged[key] = result
            else:
                merged[key] = merged[key].merge(result)

        return list(merged.values())

    @staticmethod
    def error(  # pylint: disable = too-many-arguments
        problem: ProblemInstance,
        planner: "Planner",
        config: SolveConfig,
        running_mode: RunningMode,
        computation_time: float,
        message: str,
    ) -> "PlannerResult":
        """Creates an error result.

        Args:
            problem (ProblemInstance): The erroneous problem.
            planner (Planner): The planner trying the solve the problem.
            config (SolveConfig): The configuration used to solve the problem.
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
            config,
            computation_time,
            plan_quality=None,
            error_message=message,
        )

    @staticmethod
    def not_run(
        problem: ProblemInstance,
        planner: "Planner",
        config: SolveConfig,
        running_mode: RunningMode,
    ) -> "PlannerResult":
        """Creates a not run result.

        Args:
            problem (ProblemInstance): The problem not run.
            planner (Planner): The planner trying the solve the problem.
            config (SolveConfig): The configuration used to solve the problem.
            running_mode (RunningMode): The mode used by the planner.

        Returns:
            PlannerResult: The not run result.
        """
        return PlannerResult(
            planner.name,
            problem,
            running_mode,
            PlannerResultStatus.NOT_RUN,
            config,
            computation_time=None,
            plan_quality=None,
        )

    @staticmethod
    def timeout(
        problem: ProblemInstance,
        planner: Union["Planner", str],
        config: SolveConfig,
        running_mode: RunningMode,
    ) -> "PlannerResult":
        """Creates a timeout result.

        Args:
            problem (ProblemInstance): The timed out problem.
            planner (Planner | str): The planner trying the solve the problem or its name.
            config (SolveConfig): The configuration used to solve the problem.
            running_mode (RunningMode): The mode used by the planner.

        Returns:
            PlannerResult: The timeout result.
        """
        return PlannerResult(
            str(planner),
            problem,
            running_mode,
            PlannerResultStatus.TIMEOUT,
            config,
            config.timeout,
        )

    @staticmethod
    def unsupported(
        problem: ProblemInstance,
        planner: "Planner",
        config: SolveConfig,
        running_mode: RunningMode,
    ) -> "PlannerResult":
        """Creates an unsupported result.

        Args:
            problem (ProblemInstance): The unsupported problem.
            planner (Planner): The planner trying the solve the problem.
            config (SolveConfig): The configuration used to solve the problem.
            running_mode (RunningMode): The mode used by the planner.

        Returns:
            PlannerResult: The unsupported result.
        """
        return PlannerResult(
            planner.name,
            problem,
            running_mode,
            PlannerResultStatus.UNSUPPORTED,
            config,
            computation_time=None,
            plan_quality=None,
        )


__all__ = ["PlannerResult", "PlannerResultStatus"]
