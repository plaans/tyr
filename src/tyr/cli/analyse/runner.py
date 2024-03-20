from typing import List

from tyr.cli import collector
from tyr.cli.analyse.terminal_writter import AnalyzeTerminalWritter
from tyr.cli.config import CliContext
from tyr.planners.database import Database
from tyr.planners.model.config import RunningMode, SolveConfig
from tyr.planners.model.result import PlannerResult


# pylint: disable=too-many-arguments, too-many-locals
def run_analyse(
    ctx: CliContext,
    timeout: int,
    memout: int,
    planner_filters: List[str],
    domain_filters: List[str],
    metric_filters: List[str],
):
    """Analyse the planners over the domains based on the database content.

    Args:
        ctx (CliContext): The CLI execution context.
        timeout (int): The timeout limit to use for planner results.
        memout (int): The memory out limit to use for planner results.
        planner_filters (List[str]): A list of regex filters on planner names.
        domains_filters (List[str]): A list of regex filters on problems names.
        metric_filters (List[str]): A list of regex filters on metric names.
    """

    # Create the writter and start the session.
    solve_config = SolveConfig(1, memout, timeout, True, False)
    tw = AnalyzeTerminalWritter(solve_config, ctx.out, ctx.verbosity, ctx.config)
    tw.session_starts()

    # Collect the planners and the problems to use for the analysis.
    planners = collector.collect_planners(*planner_filters)
    problems = collector.collect_problems(*domain_filters)
    metrics = collector.collect_metrics(*metric_filters)
    tw.report_collect(planners, problems, metrics)

    # Get the results from the database.
    results = []
    for pl in planners.selected:
        for pr in problems.selected:
            for rm in RunningMode:
                result = Database().load_planner_result(pl.name, pr, solve_config, rm)
                if result is None:
                    result = PlannerResult.not_run(pr, pl, solve_config, rm)
                results.append(result)
    tw.set_results(results)

    # Perform the analysis.
    tw.line()
    tw.analyse()


__all__ = ["run_analyse"]
