from tyr.cli import collector
from tyr.cli.config import CliContext
from tyr.cli.solve.terminal_writter import SolveTerminalWritter
from tyr.planners.loader import register_all_planners
from tyr.planners.model.config import RunningMode, SolveConfig


def run_solve(
    ctx: CliContext,
    solve_config: SolveConfig,
    planner_name: str,
    problem_name: str,
    running_mode: RunningMode,
):
    """Solve the given problem with the given planner.

    Args:
        ctx (CliContext): The CLI execution context.
        solve_config (SolveConfig): The configuration to use for the resolution.
        planner_name (str): The name of the planner to use.
        problem_name (str): The name of the problem to solve.
        running_mode (RunningMode): The mode to run planner resolution.
    """

    # Create the writter and start the session.
    tw = SolveTerminalWritter(solve_config, ctx.out, ctx.verbosity, ctx.config)
    tw.session_starts()

    # Collect the planner and the problem to use.
    planners = collector.collect_planners(planner_name)
    problems = collector.collect_problems(problem_name)
    if (collect := tw.report_collect(planners, problems, running_mode)) is False:
        return
    planner, problem = collect

    # Perform resolution.
    register_all_planners()
    result = planner.solve_single(problem, solve_config, running_mode)
    tw.report_result(planner, result)

    # End the session.
    tw.session_finished()


__all__ = ["run_solve"]
