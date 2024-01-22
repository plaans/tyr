# pylint: disable = missing-function-docstring, too-many-arguments

from typing import List

import click

from tyr import CliContext, RunningMode, SolveConfig, run_bench

pass_context = click.make_pass_decorator(CliContext, ensure=True)


@click.group()
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity.",
)
@click.option(
    "-o",
    "--out",
    type=click.File("w"),
    default="-",
    help="Output file. Default to stdout.",
)
@pass_context
def cli(ctx: CliContext, verbose, out):
    ctx.out = out
    ctx.verbosity = verbose


@cli.command("bench")
@click.option(
    "-t",
    "--timeout",
    default=5,
    help="Timeout for planners in seconds. Default to 5s.",
)
@click.option(
    "-m",
    "--memout",
    default=4 * 1024**3,
    help="Memout for planners in bytes. Default to 4GB.",
)
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
    timeout: int,
    memout: int,
    jobs: int,
    planners: List[str],
    domains: List[str],
    anytime: bool,
    oneshot: bool,
):
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


if __name__ == "__main__":
    cli()  # pylint: disable = no-value-for-parameter
