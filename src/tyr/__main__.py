# pylint: disable = missing-function-docstring

import click

from tyr import CliContext, SolveConfig, run_bench

pass_context = click.make_pass_decorator(CliContext, ensure=True)


@click.group()
@click.option(
    "-v",
    "--verbose",
    default=False,
    is_flag=True,
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
    ctx.verbosity += 1 if verbose else 0


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
@pass_context
def cli_bench(ctx: CliContext, timeout, memout):
    solve_config = SolveConfig(memout, timeout)
    run_bench(ctx, solve_config)


if __name__ == "__main__":
    cli()  # pylint: disable = no-value-for-parameter
