from typing import List

from tyr.cli import collector
from tyr.cli.config import CliContext
from tyr.cli.plot.terminal_writter import PlotTerminalWritter
from tyr.planners.database import Database
from tyr.planners.model.config import RunningMode, SolveConfig
from tyr.planners.model.result import PlannerResult, PlannerResultStatus


# pylint: disable=too-many-arguments, too-many-locals
def run_plot(
    ctx: CliContext,
    timeout: int,
    memout: int,
    planner_filters: List[str],
    domain_filters: List[str],
    plot_filters: List[str],
    latex: bool,
):
    """Analyse the planners over the domains based on the database content.

    Args:
        ctx (CliContext): The CLI execution context.
        timeout (int): The timeout limit to use for planner results.
        memout (int): The memory out limit to use for planner results.
        planner_filters (List[str]): A list of regex filters on planner names.
        domains_filters (List[str]): A list of regex filters on problems names.
        plot_filters (List[str]): A list of regex filters on plot names.
        latex (bool): If True, the plots will be generated in latex format.
    """
    # pylint: disable = duplicate-code

    # Create the writter and start the session.
    solve_config = SolveConfig(1, memout, timeout, True, False)
    tw = PlotTerminalWritter(solve_config, ctx.out, ctx.verbosity, ctx.config)
    tw.session_starts()

    # Collect the planners, the problems and the plots functions.
    planners = collector.collect_planners(*planner_filters)
    problems = collector.collect_problems(*domain_filters)
    plotters = collector.collect_plotters(*plot_filters)
    tw.report_collect(planners, problems, plotters)

    # Get the results from the database.
    results: List[PlannerResult] = []
    for planner in planners.selected:
        for problem in problems.selected:
            for running_mode in RunningMode:
                result = Database().load_planner_result(
                    planner.name,
                    problem,
                    solve_config,
                    running_mode,
                    keep_unsupported=True,
                )
                if result is None:
                    result = PlannerResult.not_run(
                        problem, planner, solve_config, running_mode
                    )
                results.append(result)

    # Filter the results.
    results = [
        r
        for r in results
        if not any(
            r1.status == PlannerResultStatus.NOT_RUN
            for r1 in results
            if r1.problem.name == r.problem.name and r1.running_mode == r.running_mode
        )
    ]
    for r in results:
        if r.status == PlannerResultStatus.UNSUPPORTED and not all(
            r1.status == PlannerResultStatus.UNSUPPORTED
            for r1 in results
            if r1.problem.domain == r.problem.domain
            and r1.planner_name == r.planner_name
            and r1.running_mode == r.running_mode
        ):
            msg = f"Unsupported results on domain {r.problem.domain.name} \
are not consistent for planner {r.planner_name}."
            tw.line()
            tw.write("[ERROR]", bold=True, red=True)
            tw.line(f" {msg}", red=True)
            return
    tw.report_results(results)

    # Perform the plots.
    for plotter in plotters.selected:
        if latex:
            tw.line()
            tw.line(plotter.latex(results))
        else:
            plotter.plot(results)


__all__ = ["run_plot"]
