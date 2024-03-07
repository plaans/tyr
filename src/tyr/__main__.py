# pylint: disable = missing-function-docstring, too-many-arguments

from typing import List

import click

from tyr import (  # type: ignore
    CliContext,
    RunningMode,
    SolveConfig,
    run_bench,
    run_solve,
)

# ============================================================================ #
#                                    Options                                   #
# ============================================================================ #


pass_context = click.make_pass_decorator(CliContext, ensure=True)

verbose_option = click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity.",
)
out_option = click.option(
    "-o",
    "--out",
    multiple=True,
    type=click.File("w"),
    help="Output files. Default to stdout.",
)

timeout_option = click.option(
    "-t",
    "--timeout",
    default=5,
    help="Timeout for planners in seconds. Default to 5s.",
)
memout_option = click.option(
    "-m",
    "--memout",
    default=4 * 1024**3,
    help="Memout for planners in bytes. Default to 4GB.",
)


# ============================================================================ #
#                                     Main                                     #
# ============================================================================ #


@click.group()
@verbose_option
@out_option
@pass_context
def cli(ctx: CliContext, verbose, out):
    update_context(ctx, verbose, out)


def update_context(ctx, verbose, out):
    ctx.verbosity += verbose
    ctx.out.extend(out)


# ============================================================================ #
#                                     Bench                                    #
# ============================================================================ #


@cli.command(
    "bench",
    help="Run several planners on different domains.",
)
@verbose_option
@out_option
@timeout_option
@memout_option
@click.option(
    "-j",
    "--jobs",
    default=1,
    help="Number of CPUs to use for parallel computation, \
if negative (n_cpus + 1 + jobs) are used. Default to 1.",
)
@click.option(
    "-p",
    "--planners",
    type=str,
    multiple=True,
    help="A list of regex filters on planner names.",
)
@click.option(
    "-d",
    "--domains",
    type=str,
    multiple=True,
    help="A list of regex filters on problem names. A problem name is of the form DOMAIN:UID.",
)
@click.option("--anytime", is_flag=True, help="Perform anytime solving method only.")
@click.option("--oneshot", is_flag=True, help="Perform oneshot solving method only.")
@pass_context
def cli_bench(
    ctx: CliContext,
    verbose,
    out,
    timeout: int,
    memout: int,
    jobs: int,
    planners: List[str],
    domains: List[str],
    anytime: bool,
    oneshot: bool,
):
    update_context(ctx, verbose, out)

    if anytime and oneshot:
        running_modes = [RunningMode.ANYTIME, RunningMode.ONESHOT]
    elif anytime:
        running_modes = [RunningMode.ANYTIME]
    elif oneshot:
        running_modes = [RunningMode.ONESHOT]
    else:
        running_modes = [RunningMode.ANYTIME, RunningMode.ONESHOT]

    solve_config = SolveConfig(jobs, memout, timeout)
    run_bench(ctx, solve_config, planners, domains, running_modes)


# ============================================================================ #
#                                     Solve                                    #
# ============================================================================ #


@cli.command(
    "solve",
    help="Solve a specific problem with a planner.",
)
@verbose_option
@out_option
@click.argument("planner", type=str)
@click.argument("problem", type=str)
@timeout_option
@memout_option
@click.option(
    "--fs",
    "--first-solution",
    is_flag=True,
    help="Stop the search after the first found solution.",
)
@pass_context
def cli_solve(
    ctx: CliContext,
    verbose,
    out,
    planner: str,
    problem: str,
    timeout: int,
    memout: int,
    fs: bool,
):
    update_context(ctx, verbose, out)

    running_mode = RunningMode.ONESHOT if fs else RunningMode.ANYTIME

    solve_config = SolveConfig(1, memout, timeout)
    run_solve(ctx, solve_config, planner, problem, running_mode)


if __name__ == "__main__":
    cli()  # pylint: disable = no-value-for-parameter
