from io import StringIO
from pathlib import Path
from typing import List, TextIO, Tuple
from unittest.mock import MagicMock, Mock, patch

import pytest

from tyr import (
    CliContext,
    SolveConfig,
    run_bench,
    CollectionResult,
    PlannerConfig,
    Planner,
    PlannerResult,
    PlannerResultStatus,
    AbstractDomain,
    ProblemInstance,
)


class TestBench:
    @staticmethod
    @pytest.fixture()
    def ctx():
        yield CliContext(MagicMock(TextIO), 0)

    @staticmethod
    @pytest.fixture()
    def solve_config():
        yield SolveConfig(memout=4 * 1024**3, timeout=5 * 60)

    @staticmethod
    @pytest.fixture()
    def planners():
        yield [MagicMock(Planner)] * 3

    @staticmethod
    @pytest.fixture()
    def collected_planners(planners: List[Planner]):
        yield CollectionResult(selected=planners[:2], deselected=planners[2:])

    @staticmethod
    @pytest.fixture()
    def problems():
        yield [MagicMock(ProblemInstance)] * 250

    @staticmethod
    @pytest.fixture()
    def collected_problems(problems: List[ProblemInstance]):
        yield CollectionResult(
            selected=problems[:150],
            deselected=problems[150:230],
            skipped=problems[230:],
        )

    @pytest.mark.parametrize("verbosity", [0, 1])
    @pytest.mark.parametrize("result_status", PlannerResultStatus)
    @patch("tyr.cli.bench.collector.collect_problems")
    @patch("tyr.cli.bench.collector.collect_planners")
    @patch("tyr.planners.model.result.PlannerResult.from_upf")
    @patch("unified_planning.shortcuts.OneshotPlanner")
    @patch("shutil.get_terminal_size")
    def testing(
        self,
        mocked_terminal_size: Mock,
        mocked_oneshot_planner: Mock,
        mocked_from_upf: Mock,
        mocked_collect_planners: Mock,
        mocked_collect_problems: Mock,
        result_status: PlannerResultStatus,
        verbosity: int,
        num_planners: Tuple[int, int] = (2, 1),
        num_problems: Tuple[int, int, int] = (50, 180, 20),
        num_domains: int = 5,
    ):
        out = StringIO()
        ctx = CliContext(out, verbosity)
        solve_config = SolveConfig(memout=int(4.5 * 1024**3), timeout=5 * 60 + 15)

        planners = [
            Planner(
                PlannerConfig(
                    name=f"planner-{i}",
                    problems={f"domain-{j}": f"version-{j+i}" for j in range(i + 1)},
                )
            )
            for i in range(sum(num_planners))
        ]
        collected_planners = CollectionResult(
            selected=planners[: num_planners[0]], deselected=planners[num_planners[0] :]
        )

        domains = [MagicMock(AbstractDomain) for _ in range(num_domains)]
        for i, domain in enumerate(domains):
            domain.name = f"domain-{i}"

        problems = [MagicMock(ProblemInstance) for _ in range(sum(num_problems))]
        for i, problem in enumerate(problems):
            problem.domain = domains[i % num_domains]
            problem.name = f"{problem.domain.name}:problem-{i}"
            problem.uid = str(i)
        collected_problems = CollectionResult(
            selected=problems[: num_problems[0]],
            deselected=problems[num_problems[0] : sum(num_problems[:2])],
            skipped=problems[sum(num_problems[:2]) :],
        )

        mocked_collect_planners.return_value = collected_planners
        mocked_collect_problems.return_value = collected_problems

        result = PlannerResult(
            "planner",
            problems[0],
            result_status,
            computation_time=15,
            plan="(move)",
            plan_quality=15.2654,
            error_message="My error message",
        )
        mocked_from_upf.return_value = result
        mocked_terminal_size.return_value = (120, 24)

        expected_result_path = (
            Path(__file__).parent
            / "fixtures"
            / f"{result_status.name.lower()}-{verbosity}.txt"
        )
        with open(expected_result_path, "r") as expected_result_file:
            expected_result = expected_result_file.read()

        run_bench(ctx, solve_config)
        result = out.getvalue().replace("\r", "\n")
        assert result == expected_result


# if __name__ == "__main__":

#     @patch("tyr.cli.bench.collector.collect_problems")
#     @patch("tyr.cli.bench.collector.collect_planners")
#     @patch("tyr.planners.model.result.PlannerResult.from_upf")
#     @patch("unified_planning.shortcuts.OneshotPlanner")
#     @patch("shutil.get_terminal_size")
#     def testing(
#         mocked_terminal_size: Mock,
#         mocked_oneshot_planner: Mock,
#         mocked_from_upf: Mock,
#         mocked_collect_planners: Mock,
#         mocked_collect_problems: Mock,
#         result_status: PlannerResultStatus = PlannerResultStatus.SOLVED,
#         num_planners: Tuple[int, int] = (2, 1),
#         num_problems: Tuple[int, int, int] = (50, 180, 20),
#         num_domains: int = 5,
#         verbosity: int = 0,
#     ):
#         out = open(
#             Path(__file__).parent
#             / f"fixtures/{result_status.name.lower()}-{verbosity}.txt",
#             "w",
#         )
#         # out = None
#         ctx = CliContext(out, verbosity)
#         solve_config = SolveConfig(memout=int(4.5 * 1024**3), timeout=5 * 60 + 15)

#         planners = [
#             Planner(
#                 PlannerConfig(
#                     name=f"planner-{i}",
#                     problems={f"domain-{j}": f"version-{j+i}" for j in range(i + 1)},
#                 )
#             )
#             for i in range(sum(num_planners))
#         ]
#         collected_planners = CollectionResult(
#             selected=planners[: num_planners[0]], deselected=planners[num_planners[0] :]
#         )

#         domains = [MagicMock(AbstractDomain) for _ in range(num_domains)]
#         for i, domain in enumerate(domains):
#             domain.name = f"domain-{i}"

#         problems = [MagicMock(ProblemInstance) for _ in range(sum(num_problems))]
#         for i, problem in enumerate(problems):
#             problem.domain = domains[i % num_domains]
#             problem.name = f"{problem.domain.name}:problem-{i}"
#             problem.uid = str(i)
#         collected_problems = CollectionResult(
#             selected=problems[: num_problems[0]],
#             deselected=problems[num_problems[0] : sum(num_problems[:2])],
#             skipped=problems[sum(num_problems[:2]) :],
#         )

#         mocked_collect_planners.return_value = collected_planners
#         mocked_collect_problems.return_value = collected_problems

#         result = PlannerResult(
#             "planner",
#             problems[0],
#             result_status,
#             computation_time=15,
#             plan="(move)",
#             plan_quality=15.2654,
#             error_message="My error message",
#         )
#         mocked_from_upf.return_value = result
#         mocked_terminal_size.return_value = (120, 24)

#         run_bench(ctx, solve_config)

#     for status in PlannerResultStatus:
#         for verbosity in [0, 1]:
#             testing(result_status=status, verbosity=verbosity)
#     # testing(result_status=PlannerResultStatus.SOLVED, verbosity=1)
