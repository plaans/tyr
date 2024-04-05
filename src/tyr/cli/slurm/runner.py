from typing import List, Optional

from tyr.cli import collector
from tyr.cli.config import CliContext
from tyr.cli.slurm.terminal_writter import SlurmTerminalWritter
from tyr.planners.model.config import RunningMode, SolveConfig


# pylint: disable=too-many-arguments
def run_slurm(
    ctx: CliContext,
    solve_config: SolveConfig,
    planner_filters: List[str],
    domain_filters: List[str],
    running_modes: List[RunningMode],
    user_mail: Optional[str],
    nodelist: List[str],
):
    """Create the slurm bash script to run the resolution.

    Args:
        ctx (CliContext): The CLI execution context.
        solve_config (SolveConfig): The configuration to use for the resolutions.
        jobs (int): Number of CPUs to use for parallel computation.
        planner_filters (List[str]): A list of regex filters on planner names.
        domains_filters (List[str]): A list of regex filters on problems names.
        running_modes (List[RunningMode]): A list of mode to run planner resolutions.
        user_mail (Optional[str]): The email to send the notifications.
        nodes (List[str]): The list of nodes to use on the cluster.
    """

    # Create the writter and start the session.
    tw = SlurmTerminalWritter(solve_config, ctx.out, ctx.verbosity, ctx.config)
    tw.session_starts()

    # Collect the planner and the problem to use.
    planners = collector.collect_planners(*planner_filters)
    problems = collector.collect_problems(*domain_filters)
    tw.report_collect(planners, problems)

    # Create the slurm script.
    tw.line()
    tw.script(user_mail, nodelist, running_modes)


__all__ = ["run_slurm"]
