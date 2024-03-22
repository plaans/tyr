from typing import Dict, List, Tuple
from unittest.mock import MagicMock, Mock, patch

import pytest

from tyr import (
    AbstractDomain,
    Planner,
    collect_planners,
    collect_metrics,
    collect_problems,
    collect_plotters,
    Metric,
    Plotter,
    Singleton,
)


class ProblemCache(Singleton):
    def __init__(self) -> None:
        self._cache: Dict[Tuple[AbstractDomain, str], Mock] = {}

    def get_problem(self, dom, uid):
        if (dom, uid) not in self._cache:
            problem = MagicMock()
            problem.name = f"{dom.name}:{uid}"
            problem.domain = dom
            self._cache[(dom, uid)] = problem
        return self._cache[(dom, uid)]


class TestCollectors:
    # ============================================================================ #
    #                                    Getters                                   #
    # ============================================================================ #

    @staticmethod
    @pytest.fixture()
    def all_metrics():
        metrics = [MagicMock() for _ in range(10)]
        for i, metric in enumerate(metrics):
            metric.name = f"metric-{i}"
        yield metrics

    @staticmethod
    @pytest.fixture()
    def all_planners():
        planners = [MagicMock() for _ in range(10)]
        for i, planner in enumerate(planners):
            planner.name = f"planner-{i}"
        yield planners

    @staticmethod
    @pytest.fixture()
    def all_plotters():
        plotters = [MagicMock() for _ in range(10)]
        for i, plotter in enumerate(plotters):
            plotter.name = f"plotter-{i}"
        yield plotters

    @staticmethod
    @pytest.fixture()
    def all_domains():
        domains = [MagicMock() for _ in range(10)]
        for i, domain in enumerate(domains):

            def get_problem(dom):
                return lambda x: ProblemCache().get_problem(dom, x)

            domain.name = f"domain-{i}"
            domain.get_problem = get_problem(domain)
            domain.get_num_problems.return_value = 10
        yield domains

    # ============================================================================ #
    #                                     Tests                                    #
    # ============================================================================ #

    # ================================== Metrics ================================= #

    @patch("tyr.metrics.scanner.get_all_metrics")
    def test_collect_metrics_all(
        self,
        mocked_get_all_metrics: Mock,
        all_metrics: List[Metric],
    ):
        mocked_get_all_metrics.return_value = all_metrics
        result = collect_metrics()
        assert set(result.selected) == set(all_metrics)
        assert len(set(result.deselected)) == 0
        assert len(set(result.skipped)) == 0

    @patch("tyr.metrics.scanner.get_all_metrics")
    def test_collect_metrics_one_filter(
        self,
        mocked_get_all_metrics: Mock,
        all_metrics: List[Metric],
    ):
        mocked_get_all_metrics.return_value = all_metrics
        filter1 = ".*[4-8]"

        selected = [p for p in all_metrics if int(p.name[-1]) in range(4, 9)]
        deselected = [p for p in all_metrics if int(p.name[-1]) not in range(4, 9)]

        result = collect_metrics(filter1)
        assert set(result.selected) == set(selected)
        assert set(result.deselected) == set(deselected)
        assert len(set(result.skipped)) == 0

    @patch("tyr.metrics.scanner.get_all_metrics")
    def test_collect_metrics_two_filters(
        self,
        mocked_get_all_metrics: Mock,
        all_metrics: List[Metric],
    ):
        mocked_get_all_metrics.return_value = all_metrics
        filter1 = ".*[4-8]"
        filter2 = ".*[1-5]"

        selected = [p for p in all_metrics if int(p.name[-1]) in range(1, 9)]
        deselected = [p for p in all_metrics if int(p.name[-1]) not in range(1, 9)]

        result = collect_metrics(filter1, filter2)
        assert set(result.selected) == set(selected)
        assert set(result.deselected) == set(deselected)
        assert len(set(result.skipped)) == 0

    # ================================= Planners ================================= #

    @patch("tyr.planners.scanner.get_all_planners")
    def test_collect_planners_all(
        self,
        mocked_get_all_planners: Mock,
        all_planners: List[Planner],
    ):
        mocked_get_all_planners.return_value = all_planners
        result = collect_planners()
        assert set(result.selected) == set(all_planners)
        assert len(set(result.deselected)) == 0
        assert len(set(result.skipped)) == 0

    @patch("tyr.planners.scanner.get_all_planners")
    def test_collect_planners_one_filter(
        self,
        mocked_get_all_planners: Mock,
        all_planners: List[Planner],
    ):
        mocked_get_all_planners.return_value = all_planners
        filter1 = ".*[4-8]"

        selected = [p for p in all_planners if int(p.name[-1]) in range(4, 9)]
        deselected = [p for p in all_planners if int(p.name[-1]) not in range(4, 9)]

        result = collect_planners(filter1)
        assert set(result.selected) == set(selected)
        assert set(result.deselected) == set(deselected)
        assert len(set(result.skipped)) == 0

    @patch("tyr.planners.scanner.get_all_planners")
    def test_collect_planners_two_filters(
        self,
        mocked_get_all_planners: Mock,
        all_planners: List[Planner],
    ):
        mocked_get_all_planners.return_value = all_planners
        filter1 = ".*[4-8]"
        filter2 = ".*[1-5]"

        selected = [p for p in all_planners if int(p.name[-1]) in range(1, 9)]
        deselected = [p for p in all_planners if int(p.name[-1]) not in range(1, 9)]

        result = collect_planners(filter1, filter2)
        assert set(result.selected) == set(selected)
        assert set(result.deselected) == set(deselected)
        assert len(set(result.skipped)) == 0

    # ================================= Plotters ================================= #

    @patch("tyr.plotters.scanner.get_all_plotters")
    def test_collect_plotters_all(
        self,
        mocked_get_all_plotters: Mock,
        all_plotters: List[Plotter],
    ):
        mocked_get_all_plotters.return_value = all_plotters
        result = collect_plotters()
        assert set(result.selected) == set(all_plotters)
        assert len(set(result.deselected)) == 0
        assert len(set(result.skipped)) == 0

    @patch("tyr.plotters.scanner.get_all_plotters")
    def test_collect_plotters_one_filter(
        self,
        mocked_get_all_plotters: Mock,
        all_plotters: List[Plotter],
    ):
        mocked_get_all_plotters.return_value = all_plotters
        filter1 = ".*[4-8]"

        selected = [p for p in all_plotters if int(p.name[-1]) in range(4, 9)]
        deselected = [p for p in all_plotters if int(p.name[-1]) not in range(4, 9)]

        result = collect_plotters(filter1)
        assert set(result.selected) == set(selected)
        assert set(result.deselected) == set(deselected)
        assert len(set(result.skipped)) == 0

    @patch("tyr.plotters.scanner.get_all_plotters")
    def test_collect_plotters_two_filters(
        self,
        mocked_get_all_plotters: Mock,
        all_plotters: List[Plotter],
    ):
        mocked_get_all_plotters.return_value = all_plotters
        filter1 = ".*[4-8]"
        filter2 = ".*[1-5]"

        selected = [p for p in all_plotters if int(p.name[-1]) in range(1, 9)]
        deselected = [p for p in all_plotters if int(p.name[-1]) not in range(1, 9)]

        result = collect_plotters(filter1, filter2)
        assert set(result.selected) == set(selected)
        assert set(result.deselected) == set(deselected)
        assert len(set(result.skipped)) == 0

    # ================================= Problems ================================= #

    @patch("tyr.problems.scanner.get_all_domains")
    def test_collect_problems_all(
        self,
        mocked_get_all_domain: Mock,
        all_domains: List[AbstractDomain],
    ):
        mocked_get_all_domain.return_value = all_domains
        problems = [
            d.get_problem(f"{p+1:0>2}")
            for d in all_domains
            for p in range(d.get_num_problems())
        ]
        result = collect_problems()
        assert set(result.selected) == set(problems)
        assert len(set(result.deselected)) == 0
        assert len(set(result.skipped)) == 0

    @patch("tyr.problems.scanner.get_all_domains")
    def test_collect_problems_one_filter_domain(
        self,
        mocked_get_all_domain: Mock,
        all_domains: List[AbstractDomain],
    ):
        mocked_get_all_domain.return_value = all_domains
        filter1 = ".*[4-8]:.*"

        problems = [
            d.get_problem(f"{p+1:0>2}")
            for d in all_domains
            for p in range(d.get_num_problems())
        ]
        selected = [p for p in problems if int(p.domain.name[-1]) in range(4, 9)]
        deselected = [p for p in problems if int(p.domain.name[-1]) not in range(4, 9)]

        result = collect_problems(filter1)
        assert set(result.selected) == set(selected)
        assert set(result.deselected) == set(deselected)
        assert len(set(result.skipped)) == 0

    @patch("tyr.problems.scanner.get_all_domains")
    def test_collect_problems_two_filters_domain(
        self,
        mocked_get_all_domain: Mock,
        all_domains: List[AbstractDomain],
    ):
        mocked_get_all_domain.return_value = all_domains
        filter1 = ".*[4-8]:.*"
        filter2 = ".*[1-5]:.*"

        problems = [
            d.get_problem(f"{p+1:0>2}")
            for d in all_domains
            for p in range(d.get_num_problems())
        ]
        selected = [p for p in problems if int(p.domain.name[-1]) in range(1, 9)]
        deselected = [p for p in problems if int(p.domain.name[-1]) not in range(1, 9)]

        result = collect_problems(filter1, filter2)
        assert set(result.selected) == set(selected)
        assert set(result.deselected) == set(deselected)
        assert len(set(result.skipped)) == 0

    @patch("tyr.problems.scanner.get_all_domains")
    def test_collect_problems_one_filter_problem(
        self,
        mocked_get_all_domain: Mock,
        all_domains: List[AbstractDomain],
    ):
        mocked_get_all_domain.return_value = all_domains
        filter1 = ".*:.*[4-8]"

        problems = [
            d.get_problem(f"{p+1:0>2}")
            for d in all_domains
            for p in range(d.get_num_problems())
        ]
        selected = [p for p in problems if int(p.name[-1]) in range(4, 9)]
        deselected = [p for p in problems if int(p.name[-1]) not in range(4, 9)]

        result = collect_problems(filter1)
        assert set(result.selected) == set(selected)
        assert set(result.deselected) == set(deselected)
        assert len(set(result.skipped)) == 0

    @patch("tyr.problems.scanner.get_all_domains")
    def test_collect_problems_two_filters_problem(
        self,
        mocked_get_all_domain: Mock,
        all_domains: List[AbstractDomain],
    ):
        mocked_get_all_domain.return_value = all_domains
        filter1 = ".*:.*[4-8]"
        filter2 = ".*:.*[2-5]"

        problems = [
            d.get_problem(f"{p+1:0>2}")
            for d in all_domains
            for p in range(d.get_num_problems())
        ]
        selected = [p for p in problems if int(p.name[-1]) in range(2, 9)]
        deselected = [p for p in problems if int(p.name[-1]) not in range(2, 9)]

        result = collect_problems(filter1, filter2)
        assert set(result.selected) == set(selected)
        assert set(result.deselected) == set(deselected)
        assert len(set(result.skipped)) == 0

    @patch("tyr.problems.scanner.get_all_domains")
    def test_collect_problems_skipped(
        self,
        mocked_get_all_domain: Mock,
        all_domains: List[AbstractDomain],
    ):
        for domain in all_domains:
            domain.get_problem = lambda x: None
        mocked_get_all_domain.return_value = all_domains

        problems = [
            d.get_problem(f"{p+1:0>2}")
            for d in all_domains
            for p in range(d.get_num_problems())
        ]

        result = collect_problems()
        assert len(set(result.selected)) == 0
        assert len(set(result.deselected)) == 0
        assert set(result.skipped) == set(problems)
