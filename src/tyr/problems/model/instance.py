from typing import TYPE_CHECKING, Dict, Optional

from unified_planning.plans import Plan, PlanKind
from unified_planning.shortcuts import AbstractProblem

from tyr.patterns import Lazy

if TYPE_CHECKING:
    from tyr.problems.model.domain import AbstractDomain


class ProblemInstance:
    """
    Represents an internal problem to solve.

    It is made of different versions allowing to make the problem compatible for different planners.
    The value of this versions are lazy, so the unified planning problem is only build when needed.
    """

    def __init__(self, domain: "AbstractDomain", uid: str) -> None:
        self._uid = uid
        self._domain = domain
        self._versions: Dict[str, Lazy[AbstractProblem]] = {}

    @property
    def uid(self) -> str:
        """
        Returns:
            str: The id of the problem.
        """
        return self._uid

    @property
    def domain(self) -> "AbstractDomain":
        """
        Returns:
            AbstractDomain: The domain of the problem.
        """
        return self._domain

    @property
    def versions(self) -> Dict[str, Lazy[AbstractProblem]]:
        """
        Returns:
            Dict[str, Lazy[AbstractProblem]]: The unified planning problems indexed by version name.
        """
        return self._versions

    @property
    def name(self) -> str:
        """
        Returns:
            str: The name of the problem.
        """
        return f"{self.domain.name}:{self.uid}"

    @property
    def is_empty(self) -> bool:
        """
        Returns:
            bool: Whether the problem has no versions.
        """
        return len(self.versions) == 0

    def add_version(self, version_name: str, version: Lazy[AbstractProblem]) -> None:
        """Adds a new version to the problem.

        NOTE: There is no security about overriding an existing version.

        Args:
            version_name (str): The name of the version to add.
            version (Lazy[AbstractProblem]): The lazy value of the problem version.
        """
        self._versions[version_name] = version

    def get_quality_of_plan(self, plan: Plan, version_name: str) -> Optional[float]:
        """Extracts the quality of the given plan.

        Args:
            plan (Plan): The plan to study.
            version_name (str): The name of the version to use.

        Raises:
            ValueError: When multiple quality metrics have to be measured.

        Returns:
            Optional[float]: The quality of the plan if any.
        """
        version = self.versions[version_name].value

        if (num_metrics := len(version.quality_metrics)) == 0:
            return self._get_makespan_of_plan(plan)
        if num_metrics > 1:
            raise ValueError("Multiple quality metrics is not supported")

        metric = version.quality_metrics[0]
        if metric.is_minimize_makespan():
            return self._get_makespan_of_plan(plan)
        return self.domain.get_quality_of_plan(plan)

    def _get_makespan_of_plan(self, plan: Plan) -> Optional[float]:
        if plan.kind == PlanKind.TIME_TRIGGERED_PLAN:
            return float(max(s + (d or 0) for (s, _, d) in plan.timed_actions))
        if plan.kind == PlanKind.SEQUENTIAL_PLAN:
            return len(plan.actions)
        if plan.kind == PlanKind.SCHEDULE:
            return float(
                max(float(str(plan.assignment[a.end])) for a in plan.activities)
            )
        if plan.kind == PlanKind.HIERARCHICAL_PLAN:
            return self._get_makespan_of_plan(plan.action_plan)
        return None


__all__ = ["ProblemInstance"]
