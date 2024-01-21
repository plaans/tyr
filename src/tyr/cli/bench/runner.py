from typing import Dict, List

from tyr.cli.bench import collector
from tyr.cli.bench.terminal_writter import BenchTerminalWritter
from tyr.cli.config import CliContext
from tyr.planners.model.config import SolveConfig
from tyr.problems.model.domain import AbstractDomain
from tyr.problems.model.instance import ProblemInstance


def run_bench(ctx: CliContext, solve_config: SolveConfig):
    """Compares a set of planners over a bench of problems.

    Args:
        ctx (CliContext): The CLI execution context.
        solve_config (SolveConfig): The configuration to use for the resolutions.
    """

    # Create the writter and start the session.
    tw = BenchTerminalWritter(solve_config, ctx.out, ctx.verbosity)
    tw.session_starts()

    # Collect the planners and the problems to use for the benchmark.
    planners, problems = collector.collect_planners(), collector.collect_problems()
    tw.report_collect(planners, problems)

    # Group problems by domains.
    pb_by_dom: Dict[AbstractDomain, List[ProblemInstance]] = {}
    for problem in problems.selected:
        pb_by_dom.setdefault(problem.domain, []).append(problem)

    # Get domain names in alphabetical order.
    domains = sorted(pb_by_dom.keys(), key=lambda d: d.name)

    # Perform resolution.
    for domain in domains:
        tw.report_domain(domain)

        for planner in planners.selected:
            tw.report_planner(planner)

            for problem in pb_by_dom[domain]:
                result = planner.solve(problem, solve_config)
                tw.report_planner_result(result)
            tw.report_planner_finished()

    tw.session_finished()
