from dataclasses import dataclass, field
from typing import Generic, List, TypeVar

from tyr.planners.loader import register_all_planners
from tyr.planners.model.planner import Planner
from tyr.planners.scanner import get_all_planners
from tyr.problems.model.instance import ProblemInstance
from tyr.problems.scanner import get_all_domains

T = TypeVar("T")


@dataclass
class CollectionResult(Generic[T]):
    """Stores the result of a collection."""

    selected: List[T] = field(default_factory=list)
    deselected: List[T] = field(default_factory=list)
    skipped: List[None] = field(default_factory=list)

    @property
    def total(self) -> int:
        """
        Returns:
            int: The total number of collected items.
        """
        return len(self.selected) + len(self.deselected) + len(self.skipped)


def collect_planners() -> CollectionResult[Planner]:
    """
    Returns:
        CollectionResult[Planner]: The collected planners for the benchmark.
    """
    # TODO - Filter planners
    register_all_planners()
    return CollectionResult(selected=get_all_planners())


def collect_problems() -> CollectionResult[ProblemInstance]:
    """
    Returns:
        CollectionResult[Planner]: The collected problems for the benchmark.
    """
    # TODO - Filter problems
    problems = [
        d.get_problem(f"{p+1:0>2}")
        for d in get_all_domains()
        for p in range(d.get_num_problems())
    ]
    return CollectionResult(
        selected=[p for p in problems if p is not None],
        skipped=[p for p in problems if p is None],
    )
