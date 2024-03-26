# pylint: disable = missing-function-docstring, too-many-arguments, too-many-locals

from pathlib import Path
from typing import List, Optional

import click

from tyr import (  # type: ignore
    CliContext,
    RunningMode,
    SolveConfig,
    load_config,
    run_bench,
    run_solve,
    run_table,
)
from tyr.cli.plot.runner import run_plot

# ============================================================================ #
#                                 Configuration                                #
# ============================================================================ #

DEFAULT_CONFIG = {
    # Default
    "memout": 4 * 1024**3,
    "timeout": 5,
    "verbose": 0,
    "quiet": 0,
    "out": [],
    # Bench
    "jobs": 1,
    "planners": [],
    "domains": [],
    "anytime": False,
    "oneshot": False,
    "db_only": False,
    "no_db": False,
    # Plot
    "plotters": [],
    # Solve
    "planner": "",
    "problem": "",
    "fs": False,
    # Table
    "metrics": [],
    "best_column": False,
    "best_row": False,
    "latex": False,
    "latex_caption": "Table of metrics.",
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


def yaml_config(path: Optional[Path], name: str) -> dict:
    config = load_config("cli", path)
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
quiet_option = click.option(
    "-q",
    "--quiet",
    count=True,
    help="Decrease verbosity.",
)
out_option = click.option(
    "-o",
    "--out",
    multiple=True,
    type=click.File("w"),
    help="Output files. Default to stdout.",
)
config_option = click.option(
    "-c",
    "--config",
    type=click.Path(exists=True),
    help="Path to a configuration file.",
)

timeout_option = click.option(
    "-t",
    "--timeout",
    type=int,
    help=f"Timeout for planners in seconds. Default to {DEFAULT_CONFIG['timeout']}s.",
)
memout_option = click.option(
    "-m",
    "--memout",
    type=int,
    help="Memout for planners in bytes. Default to 4GB.",
)

latex_option = click.option(
    "--latex",
    is_flag=True,
    help="Generate LaTeX code of the result.",
)

planners_filter = click.option(
    "-p",
    "--planners",
    type=str,
    multiple=True,
    help="A list of regex filters on planner names.",
)
domains_filter = click.option(
    "-d",
    "--domains",
    type=str,
    multiple=True,
    help="A list of regex filters on domain names. A domain name is of the form DOMAIN:UID.",
)
metrics_filter = click.option(
    "-M",
    "--metrics",
    type=str,
    multiple=True,
    help="A list of regex filters on metric names.",
)
plotters_filter = click.option(
    "-P",
    "--plotters",
    type=str,
    multiple=True,
    help="A list of regex filters on plotter names.",
)


# ============================================================================ #
#                                     Main                                     #
# ============================================================================ #


@click.group(chain=True)
@verbose_option
@quiet_option
@out_option
@config_option
@pass_context
def cli(ctx: CliContext, verbose, quiet, out, config):
    update_context(ctx, verbose, quiet, out, config)


def update_context(ctx, verbose, quiet, out, config):
    ctx.verbosity += verbose - quiet
    ctx.out.extend(out)
    ctx.config = config


# ============================================================================ #
#                                     Bench                                    #
# ============================================================================ #


@cli.command(
    "bench",
    help="Run several planners on different domains and save results in the database.",
)
@verbose_option
@quiet_option
@out_option
@config_option
@timeout_option
@memout_option
@click.option(
    "-j",
    "--jobs",
    type=int,
    help=f"Number of CPUs to use for parallel computation, \
if negative (n_cpus + 1 + jobs) are used. Default to {DEFAULT_CONFIG['jobs']}.",
)
@planners_filter
@domains_filter
@click.option("--anytime", is_flag=True, help="Perform anytime solving method only.")
@click.option("--oneshot", is_flag=True, help="Perform oneshot solving method only.")
@click.option("--db-only", is_flag=True, help="Only use the database for results.")
@click.option("--no-db", is_flag=True, help="Do not use the database for results.")
@pass_context
def cli_bench(
    ctx: CliContext,
    verbose: int,
    quiet: int,
    out,
    config,
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
    config = config or ctx.config
    cli_config = {
        "verbose": verbose,
        "quiet": quiet,
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
    conf = merge_configs(cli_config, yaml_config(config, "bench"), DEFAULT_CONFIG)

    update_context(ctx, conf["verbose"], conf["quiet"], conf["out"], config)

    if conf["anytime"] and conf["oneshot"]:
        running_modes = [RunningMode.ANYTIME, RunningMode.ONESHOT]
    elif conf["anytime"]:
        running_modes = [RunningMode.ANYTIME]
    elif conf["oneshot"]:
        running_modes = [RunningMode.ONESHOT]
    else:
        running_modes = [RunningMode.ANYTIME, RunningMode.ONESHOT]

    if conf["db_only"] and conf["no_db"]:
        raise click.BadOptionUsage(
            "--db-only --no-db",
            "Cannot use both --db-only and --no-db.",
        )

    solve_config = SolveConfig(
        conf["jobs"],
        conf["memout"],
        conf["timeout"],
        conf["db_only"],
        conf["no_db"],
    )

    run_bench(ctx, solve_config, conf["planners"], conf["domains"], running_modes)


# ============================================================================ #
#                                     Plot                                     #
# ============================================================================ #


@cli.command(
    "plot",
    help="Plot the results stored in the database.",
)
@verbose_option
@quiet_option
@out_option
@config_option
@timeout_option
@memout_option
@planners_filter
@domains_filter
@plotters_filter
@latex_option
@pass_context
def cli_plot(
    ctx: CliContext,
    verbose: int,
    quiet: int,
    out,
    config,
    timeout: int,
    memout: int,
    planners: List[str],
    domains: List[str],
    plotters: List[str],
    latex: bool,
):
    config = config or ctx.config
    cli_config = {
        "verbose": verbose,
        "quiet": quiet,
        "out": out,
        "timeout": timeout,
        "memout": memout,
        "planners": planners,
        "domains": domains,
        "plotters": plotters,
        "latex": latex,
    }
    conf = merge_configs(cli_config, yaml_config(config, "plot"), DEFAULT_CONFIG)

    update_context(ctx, conf["verbose"], conf["quiet"], conf["out"], config)
    run_plot(
        ctx,
        conf["timeout"],
        conf["memout"],
        conf["planners"],
        conf["domains"],
        conf["plotters"],
        conf["latex"],
    )


# ============================================================================ #
#                                     Solve                                    #
# ============================================================================ #


@cli.command(
    "solve",
    help="Solve a specific problem with a planner.",
)
@verbose_option
@quiet_option
@out_option
@config_option
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
    quiet: int,
    out,
    config,
    planner: str,
    problem: str,
    timeout: int,
    memout: int,
    fs: bool,
):
    config = config or ctx.config
    cli_config = {
        "verbose": verbose,
        "quiet": quiet,
        "out": out,
        "planner": planner,
        "problem": problem,
        "timeout": timeout,
        "memout": memout,
        "fs": fs,
    }
    conf = merge_configs(cli_config, yaml_config(config, "solve"), DEFAULT_CONFIG)

    if conf["planner"] == "":
        raise click.BadArgumentUsage("Missing argument 'PLANNER'.")
    if conf["problem"] == "":
        raise click.BadArgumentUsage("Missing argument 'PROBLEM'.")

    update_context(ctx, conf["verbose"], conf["quiet"], conf["out"], config)

    running_mode = RunningMode.ONESHOT if conf["fs"] else RunningMode.ANYTIME

    solve_config = SolveConfig(1, conf["memout"], conf["timeout"], False, True)
    run_solve(ctx, solve_config, conf["planner"], conf["problem"], running_mode)


# ============================================================================ #
#                                     Table                                    #
# ============================================================================ #


@cli.command(
    "table",
    help="Analyse the results stored in the database.",
)
@verbose_option
@quiet_option
@out_option
@config_option
@timeout_option
@memout_option
@planners_filter
@domains_filter
@metrics_filter
@click.option("--best-col", is_flag=True, help="Print the best metrics on the right.")
@click.option("--best-row", is_flag=True, help="Print the best metrics on the bottom.")
@latex_option
@click.option("--latex-caption", type=str, help="Caption for the LaTeX table.")
@pass_context
def cli_table(
    ctx: CliContext,
    verbose: int,
    quiet: int,
    out,
    config,
    timeout: int,
    memout: int,
    planners: List[str],
    domains: List[str],
    metrics: List[str],
    best_col: bool,
    best_row: bool,
    latex: bool,
    latex_caption: str,
):
    config = config or ctx.config
    cli_config = {
        "verbose": verbose,
        "quiet": quiet,
        "out": out,
        "timeout": timeout,
        "memout": memout,
        "planners": planners,
        "domains": domains,
        "metrics": metrics,
        "best_column": best_col,
        "best_row": best_row,
        "latex": latex,
        "latex_caption": latex_caption,
    }
    conf = merge_configs(cli_config, yaml_config(config, "table"), DEFAULT_CONFIG)

    update_context(ctx, conf["verbose"], conf["quiet"], conf["out"], config)
    run_table(
        ctx,
        conf["timeout"],
        conf["memout"],
        conf["planners"],
        conf["domains"],
        conf["metrics"],
        conf["best_column"],
        conf["best_row"],
        conf["latex"],
        conf["latex_caption"],
    )


if __name__ == "__main__":
    cli()  # pylint: disable = no-value-for-parameter
