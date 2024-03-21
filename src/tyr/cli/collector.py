import re
from dataclasses import dataclass, field
from typing import Callable, Generic, List, TypeVar

from tyr import plotters
from tyr.metrics import scanner as metric_scanner
from tyr.metrics.metric import Metric
from tyr.planners import scanner as planner_scanner
from tyr.planners.model.planner import Planner
from tyr.planners.model.result import PlannerResult
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


def collect_metrics(*filters: str) -> CollectionResult[Metric]:
    """
    Args:
        filters (List[str]): A list of regex filters on metric names.

    Returns:
        CollectionResult[Metric]: The collected metrics for the benchmark.
    """
    all_metrics = metric_scanner.get_all_metrics()
    selected: List[Metric] = []

    if len(filters) == 0:
        return CollectionResult(all_metrics)

    for flt in filters:
        re_filter = re.compile(flt)

        for metric in all_metrics:
            if re_filter.match(metric.name) is not None:
                selected.append(metric)

    selected = list(set(selected))  # Remove duplicates
    deselected = [m for m in all_metrics if m not in selected]

    return CollectionResult(selected, deselected)


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


def collect_plotters(
    *filters: str,
) -> CollectionResult[Callable[[List[PlannerResult]], None]]:
    """
    Args:
        filters (List[str]): A list of regex filters on plot names.

    Returns:
        CollectionResult[Callable[[List[PlannerResult]], None]]: The collected plots.
    """
    all_plots = plotters.get_all_plotters()
    selected: List[Callable[[List[PlannerResult]], None]] = []

    if len(filters) == 0:
        return CollectionResult(all_plots)

    for flt in filters:
        re_filter = re.compile(flt)

        for plot in all_plots:
            if re_filter.match(plot.__name__) is not None:
                selected.append(plot)

    selected = list(set(selected))  # Remove duplicates
    deselected = [p for p in all_plots if p not in selected]

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


__all__ = [
    "collect_metrics",
    "collect_planners",
    "collect_plotters",
    "collect_problems",
    "CollectionResult",
]
