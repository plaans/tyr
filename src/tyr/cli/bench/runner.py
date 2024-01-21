from typing import Dict, List, TypeVar

from tyr.cli.bench import collector
from tyr.cli.bench.terminal_writter import BenchTerminalWritter
from tyr.cli.config import CliContext
from tyr.planners.model.config import SolveConfig
from tyr.problems.model.domain import AbstractDomain
from tyr.problems.model.instance import ProblemInstance

T = TypeVar("T")


def sort_items(items: List[T]) -> List[T]:
    return sorted(
        items,
        key=lambda x: (x.name.split(":")[0], int(x.name.split(":")[1]))  # type: ignore
        if ":" in x.name  # type: ignore
        else x.name,  # type: ignore
    )


def run_bench(
    ctx: CliContext,
    solve_config: SolveConfig,
    planner_filters: List[str],
    domain_filters: List[str],
):
    """Compares a set of planners over a bench of problems.

    Args:
        ctx (CliContext): The CLI execution context.
        solve_config (SolveConfig): The configuration to use for the resolutions.
        planner_filters (List[str]): A list of regex filters on planner names.
        domains_filters (List[str]): A list of regex filters on problems names.
    """

    # Create the writter and start the session.
    tw = BenchTerminalWritter(solve_config, ctx.out, ctx.verbosity)
    tw.session_starts()

    # Collect the planners and the problems to use for the benchmark.
    planners = collector.collect_planners(*planner_filters)
    problems = collector.collect_problems(*domain_filters)
    tw.report_collect(planners, problems)

    # Group problems by domains.
    pb_by_dom: Dict[AbstractDomain, List[ProblemInstance]] = {}
    for problem in problems.selected:
        pb_by_dom.setdefault(problem.domain, []).append(problem)

    # Sort all loop lists on alphabetical order.
    srtd_domains = sort_items(list(pb_by_dom.keys()))
    srtd_planners = sort_items(planners.selected)
    for domain in pb_by_dom:
        pb_by_dom[domain] = sort_items(pb_by_dom[domain])

    # Perform resolution.
    for domain in srtd_domains:
        tw.report_domain(domain)

        for planner in srtd_planners:
            tw.report_planner(planner)

            for problem in pb_by_dom[domain]:
                result = planner.solve(problem, solve_config)
                tw.report_planner_result(result)
            tw.report_planner_finished()

    tw.session_finished()
