from typing import List

from tyr.cli import collector
from tyr.cli.config import CliContext
from tyr.cli.vbp.terminal_writer import VbpTerminalWriter
from tyr.planners.database import Database
from tyr.planners.model.config import RunningMode, SolveConfig
from tyr.planners.model.result import PlannerResult, PlannerResultStatus


# pylint: disable=too-many-arguments, too-many-positional-arguments, too-many-locals
def run_vbp(
    ctx: CliContext,
    timeout: int,
    memout: int,
    planner_group_filters: List[List[str]],
    domain_filters: List[str],
    metric_filters: List[str],
    colored: bool,
    latex: bool,
    latex_array_stretch: float,
    latex_caption: str,
    latex_font_size: str,
    latex_horizontal_space: float,
    latex_pos: str,
    latex_star: bool,
):
    """
    Analyse the planners over the domains based on the database content
    in a Virtual Best Planner approach.

    Args:
        ctx (CliContext): The CLI execution context.
        timeout (int): The timeout limit to use for planner results.
        memout (int): The memory out limit to use for planner results.
        planner_group_filters (List[List[str]]): A list of regex filters on planners for each group.
        domains_filters (List[str]): A list of regex filters on problems names.
        metric_filters (List[str]): A list of regex filters on metric names.
        colored (bool): Whether to use colored output.
        latex (bool): Whether to print the table in LaTeX format.
        latex_array_stretch (float): The stretch factor to use for the LaTeX array.
        latex_caption (str): The caption to use for the LaTeX table.
        latex_font_size (str): The font size to use for the LaTeX table.
        latex_horizontal_space (float): The horizontal space for the LaTeX table in cm.
        latex_pos (str): The position to use for the LaTeX table.
        latex_star (bool): Whether to use a table* environment in LaTeX rather than a table one.
    """
    # pylint: disable = duplicate-code

    # Create the writer and start the session.
    solve_config = SolveConfig(1, memout, timeout, 0, True, False, True, False)
    tw = VbpTerminalWriter(
        solve_config,
        ctx.out,
        ctx.verbosity,
        ctx.config,
        colored,
        latex,
        latex_array_stretch,
        latex_caption,
        latex_font_size,
        latex_horizontal_space,
        latex_pos,
        latex_star,
    )
    tw.session_starts()

    # Collect the planners, the problems, and the metrics to use for the analysis.
    groups = [
        collector.collect_planners(*group_filters)
        for group_filters in planner_group_filters
    ]
    problems = collector.collect_problems(*domain_filters)
    metrics = collector.collect_metrics(*metric_filters)
    tw.report_collect(groups, problems, metrics)

    # Get the results from the database.
    results: List[List[PlannerResult]] = []
    for group in groups:
        requests = [
            (planner, problem, running_mode)
            for planner in group.selected
            for problem in problems.selected
            for running_mode in RunningMode
            if running_mode != RunningMode.MERGED
        ]
        group_results: List[PlannerResult] = list(
            Database().load_multi_planner_results(  # type: ignore
                requests,  # type: ignore
                solve_config,
                keep_unsupported=True,
                not_run_by_default=True,
            )
        )
        assert not any(r is None for r in group_results)  # nosec: B101
        results.append(group_results)

    # Filter the results.
    results = [
        [
            r
            for r in group_results
            if not any(
                r1.status == PlannerResultStatus.NOT_RUN
                for r1 in group_results
                if r1.problem.name == r.problem.name
                and r1.running_mode == r.running_mode
            )
        ]
        for group_results in results
    ]
    for group_results in results:
        for r in group_results:
            if r.status == PlannerResultStatus.UNSUPPORTED and not all(
                r1.status == PlannerResultStatus.UNSUPPORTED
                for r1 in group_results
                if r1.problem.domain == r.problem.domain
                and r1.planner.name == r.planner.name
                and r1.running_mode == r.running_mode
            ):
                msg = f"Unsupported results on domain {r.problem.domain.name} \
    are not consistent for planner {r.planner}."
                tw.line()
                tw.write("[ERROR]", bold=True, red=True)
                tw.line(f" {msg}", red=True)
                return
    tw.set_results(results)

    # Perform the analysis.
    tw.line()
    if len(results) == 0:
        tw.write("[WARNING]", bold=True, yellow=True)
        tw.line(" No results to analyse.")
    else:
        tw.analyse()


__all__ = ["run_vbp"]
