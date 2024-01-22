import re
from dataclasses import dataclass, field
from typing import Generic, List, TypeVar

from tyr.planners import scanner as planner_scanner
from tyr.planners.model.planner import Planner
from tyr.problems import scanner as domain_scanner
from tyr.problems.model.instance import ProblemInstance

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


def collect_planners(*filters: str) -> CollectionResult[Planner]:
    """
    Args:
        filters (List[str]): A list of regex filters on planner names.

    Returns:
        CollectionResult[Planner]: The collected planners for the benchmark.
    """
    all_planners = planner_scanner.get_all_planners()
    selected: List[Planner] = []

    if len(filters) == 0:
        return CollectionResult(all_planners)

    for flt in filters:
        re_filter = re.compile(flt)

        for planner in all_planners:
            if re_filter.match(planner.name) is not None:
                selected.append(planner)

    selected = list(set(selected))  # Remove duplicates
    deselected = [p for p in all_planners if p not in selected]

    return CollectionResult(selected, deselected)


def collect_problems(*filters: str) -> CollectionResult[ProblemInstance]:
    """

    Args:
        filters (List[str]): A list of regex filters on problem names.

    Returns:
        CollectionResult[Planner]: The collected problems for the benchmark.
    """
    all_problems = [
        d.get_problem(f"{p+1:0>2}")
        for d in domain_scanner.get_all_domains()
        for p in range(d.get_num_problems())
    ]
    skipped = [p for p in all_problems if p is None]
    available = [p for p in all_problems if p is not None]
    selected: List[ProblemInstance] = []

    if len(filters) == 0:
        return CollectionResult(available, [], skipped)

    for flt in filters:
        re_filter = re.compile(flt)

        for problem in available:
            if re_filter.match(problem.name) is not None:
                selected.append(problem)

    selected = list(set(selected))  # Remove duplicates
    desectected = [p for p in available if p not in selected]
    return CollectionResult(selected, desectected, skipped)
