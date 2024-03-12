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
from tyr.configuration.loader import load_config

# ============================================================================ #
#                                 Configuration                                #
# ============================================================================ #

DEFAULT_CONFIG = {
    # Default
    "memout": 4 * 1024**3,
    "timeout": 5,
    "verbose": 0,
    "out": [],
    # Bench
    "jobs": 1,
    "planners": [],
    "domains": [],
    "anytime": False,
    "oneshot": False,
    "db_only": False,
    "no_db": False,
    # Solve
    "planner": "",
    "problem": "",
    "fs": False,
}


def merge_configs(cli_config: dict, file_config: dict, default_config: dict) -> dict:
    config = default_config.copy()
    config.update(file_config)

    for k, v in cli_config.items():
        if isinstance(v, (list, tuple)):
            if list(v) != list(default_config[k]):
                config[k] = v
        elif v is not None and v != default_config[k]:
            config[k] = v

    return config


def yaml_config(name: str) -> dict:
    config = load_config("cli")
    if name in config:
        return config[name] or {}
    return {}


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
    help=f"Timeout for planners in seconds. Default to {DEFAULT_CONFIG['timeout']}s.",
)
memout_option = click.option(
    "-m",
    "--memout",
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
    help=f"Number of CPUs to use for parallel computation, \
if negative (n_cpus + 1 + jobs) are used. Default to {DEFAULT_CONFIG['jobs']}.",
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
@click.option("--db-only", is_flag=True, help="Only use the database for results.")
@click.option("--no-db", is_flag=True, help="Do not use the database for results.")
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
    db_only: bool,
    no_db: bool,
):
    cli_config = {
        "verbose": verbose,
        "out": out,
        "timeout": timeout,
        "memout": memout,
        "jobs": jobs,
        "planners": planners,
        "domains": domains,
        "anytime": anytime,
        "oneshot": oneshot,
        "db_only": db_only,
        "no_db": no_db,
    }
    config = merge_configs(cli_config, yaml_config("bench"), DEFAULT_CONFIG)

    update_context(ctx, config["verbose"], config["out"])

    if config["anytime"] and config["oneshot"]:
        running_modes = [RunningMode.ANYTIME, RunningMode.ONESHOT]
    elif config["anytime"]:
        running_modes = [RunningMode.ANYTIME]
    elif config["oneshot"]:
        running_modes = [RunningMode.ONESHOT]
    else:
        running_modes = [RunningMode.ANYTIME, RunningMode.ONESHOT]

    if config["db_only"] and config["no_db"]:
        raise click.BadOptionUsage(
            "--db-only --no-db",
            "Cannot use both --db-only and --no-db.",
        )

    solve_config = SolveConfig(
        config["jobs"],
        config["memout"],
        config["timeout"],
        config["db_only"],
        config["no_db"],
    )

    run_bench(ctx, solve_config, config["planners"], config["domains"], running_modes)


# ============================================================================ #
#                                     Solve                                    #
# ============================================================================ #


@cli.command(
    "solve",
    help="Solve a specific problem with a planner.",
)
@verbose_option
@out_option
@click.argument("planner", type=str, required=False)
@click.argument("problem", type=str, required=False)
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
    cli_config = {
        "verbose": verbose,
        "out": out,
        "planner": planner,
        "problem": problem,
        "timeout": timeout,
        "memout": memout,
        "fs": fs,
    }
    config = merge_configs(cli_config, yaml_config("solve"), DEFAULT_CONFIG)

    if config["planner"] == "":
        raise click.BadArgumentUsage("Missing argument 'PLANNER'.")
    if config["problem"] == "":
        raise click.BadArgumentUsage("Missing argument 'PROBLEM'.")

    update_context(ctx, config["verbose"], config["out"])

    running_mode = RunningMode.ONESHOT if config["fs"] else RunningMode.ANYTIME

    solve_config = SolveConfig(1, config["memout"], config["timeout"], False, True)
    run_solve(ctx, solve_config, config["planner"], config["problem"], running_mode)


if __name__ == "__main__":
    cli()  # pylint: disable = no-value-for-parameter
