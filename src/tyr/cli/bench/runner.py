import multiprocessing
from typing import Dict, List, TypeVar

from joblib import Parallel, delayed

from tyr.cli.bench import collector
from tyr.cli.bench.terminal_writter import BenchResult, BenchTerminalWritter
from tyr.cli.config import CliContext
from tyr.planners.loader import register_all_planners
from tyr.planners.model.config import RunningMode, SolveConfig
from tyr.planners.model.planner import Planner
from tyr.problems.model.domain import AbstractDomain
from tyr.problems.model.instance import ProblemInstance

I = TypeVar("I")  # noqa: E741


# pylint: disable = too-many-arguments
def _solve(
    tw: BenchTerminalWritter,
    results: List[BenchResult],
    planner: Planner,
    problem: ProblemInstance,
    solve_config: SolveConfig,
    running_mode: RunningMode,
):
    register_all_planners()
    result = planner.solve(problem, solve_config, running_mode)
    tw.set_results(results)
    tw.report_planner_result(problem.domain, planner, result)


def _sort_items(items: List[I]) -> List[I]:
    return sorted(
        items,
        key=lambda x: (x.name.split(":")[0], int(x.name.split(":")[1]))  # type: ignore
        if ":" in x.name  # type: ignore
        else x.name,  # type: ignore
    )


# pylint: disable = too-many-locals
def run_bench(
    ctx: CliContext,
    solve_config: SolveConfig,
    planner_filters: List[str],
    domain_filters: List[str],
    running_modes: List[RunningMode],
):
    """Compares a set of planners over a bench of problems.

    Args:
        ctx (CliContext): The CLI execution context.
        solve_config (SolveConfig): The configuration to use for the resolutions.
        jobs (int): Number of CPUs to use for parallel computation.
        planner_filters (List[str]): A list of regex filters on planner names.
        domains_filters (List[str]): A list of regex filters on problems names.
        running_modes (List[RunningMode]): A list of mode to run planner resolutions.
    """

    # Create the writter and start the session.
    tw = BenchTerminalWritter(solve_config, ctx.out, ctx.verbosity)
    tw.session_starts()

    # Collect the planners and the problems to use for the benchmark.
    planners = collector.collect_planners(*planner_filters)
    problems = collector.collect_problems(*domain_filters)
    tw.report_collect(planners, problems, running_modes)

    # Group problems by domains.
    pb_by_dom: Dict[AbstractDomain, List[ProblemInstance]] = {}
    for problem in problems.selected:
        pb_by_dom.setdefault(problem.domain, []).append(problem)

    # Sort all loop lists on alphabetical order.
    srtd_domains = _sort_items(list(pb_by_dom.keys()))
    srtd_planners = _sort_items(planners.selected)
    for domain in pb_by_dom:
        pb_by_dom[domain] = _sort_items(pb_by_dom[domain])

    # Perform resolution.
    results: List[BenchResult] = []
    if solve_config.jobs == 1:
        for running_mode in running_modes:
            tw.report_running_mode(running_mode)

            for domain in srtd_domains:
                tw.report_domain(domain)

                for planner in srtd_planners:
                    tw.report_planner(domain, planner)

                    for problem in pb_by_dom[domain]:
                        _solve(
                            tw,
                            results,
                            planner,
                            problem,
                            solve_config,
                            running_mode,
                        )
                    tw.report_planner_finished()

    else:
        tw.line()

        with multiprocessing.Manager() as manager:
            shared_results = manager.list(results)
            Parallel(n_jobs=solve_config.jobs)(
                delayed(_solve)(
                    tw,
                    shared_results,
                    planner,
                    problem,
                    solve_config,
                    running_mode,
                )
                for running_mode in running_modes
                for domain in srtd_domains
                for planner in srtd_planners
                for problem in pb_by_dom[domain]
            )
            results = shared_results[:]

    # End the session.
    tw.set_results(results)
    tw.session_finished()
