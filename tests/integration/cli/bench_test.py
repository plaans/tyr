import os
import platform
import sys
from io import StringIO
from pathlib import Path
from typing import List, TextIO, Tuple
from unittest.mock import MagicMock, Mock, patch

import pytest

from tyr import (
    AbstractDomain,
    CliContext,
    CollectionResult,
    Planner,
    PlannerConfig,
    PlannerResult,
    PlannerResultStatus,
    ProblemInstance,
    SolveConfig,
    run_bench,
)
from tyr.planners.model.config import RunningMode


class TestBench:
    @staticmethod
    @pytest.fixture()
    def ctx():
        yield CliContext(MagicMock(TextIO), 0)

    @staticmethod
    @pytest.fixture()
    def solve_config():
        yield SolveConfig(jobs=1, memout=4 * 1024**3, timeout=5 * 60)

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
    @pytest.mark.parametrize("running_mode", RunningMode)
    @patch("tyr.cli.bench.collector.collect_problems")
    @patch("tyr.cli.bench.collector.collect_planners")
    @patch("tyr.planners.model.result.PlannerResult.from_upf")
    @patch("unified_planning.shortcuts.AnytimePlanner")
    @patch("unified_planning.shortcuts.OneshotPlanner")
    @patch("shutil.get_terminal_size")
    @patch("time.time", return_value=0)
    def testing(
        self,
        mocked_time: Mock,
        mocked_terminal_size: Mock,
        mocked_oneshot_planner: Mock,
        mocked_anytime_planner: Mock,
        mocked_from_upf: Mock,
        mocked_collect_planners: Mock,
        mocked_collect_problems: Mock,
        result_status: PlannerResultStatus,
        running_mode: RunningMode,
        verbosity: int,
        num_planners: Tuple[int, int] = (2, 1),
        num_problems: Tuple[int, int, int] = (50, 180, 20),
        num_domains: int = 5,
    ):
        out = StringIO()
        ctx = CliContext(out, verbosity)
        solve_config = SolveConfig(
            jobs=1,
            memout=int(4.5 * 1024**3),
            timeout=5 * 60 + 15,
        )

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
            problem.name = f"{problem.domain.name}:{i}"
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
            running_mode,
            result_status,
            computation_time=15,
            plan_quality=15.2654,
            error_message="My error message",
        )
        mocked_from_upf.return_value = result
        mocked_terminal_size.return_value = (120, 24)

        if result_status != PlannerResultStatus.SOLVED:
            mocked_oneshot_planner.return_value.__enter__.return_value.solve.return_value = (
                None
            )
            mocked_anytime_planner.return_value.__enter__.return_value.solve.return_value = (
                None
            )

        expected_result_path = (
            Path(__file__).parent
            / "fixtures"
            / f"{result_status.name.lower()}-{verbosity}-{running_mode.name.lower()}.txt"
        )
        with open(expected_result_path, "r") as expected_result_file:
            expected_result = expected_result_file.read()
        stuff = f"platform {sys.platform} -- Python {platform.python_version()} -- {sys.executable}"
        stuff += f"\nrootdir: {os.getcwd()}"
        expected_result = expected_result.format(machine_stuff=stuff)

        run_bench(ctx, solve_config, [], [], [running_mode])
        result = out.getvalue().replace("\r", "\n")
        assert result == expected_result
