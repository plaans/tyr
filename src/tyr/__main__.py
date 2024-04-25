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
from tyr.cli.slurm.runner import run_slurm
from tyr.core.paths import TyrPaths

# ============================================================================ #
#                                 Configuration                                #
# ============================================================================ #

DEFAULT_CONFIG = {
    "anytime": False,
    "best_column": False,
    "best_row": False,
    "db_only": False,
    "db_path": "",
    "domains": [],
    "fs": False,
    "jobs": 1,
    "latex": False,
    "latex_array_stretch": 1.2,
    "latex_caption": "Table of metrics.",
    "latex_font_size": "footnotesize",
    "latex_horizontal_space": 0.35,
    "latex_pos": "htb",
    "latex_star": False,
    "logs_path": "",
    "memout": 4 * 1024**3,
    "metrics": [],
    "no_db_load": False,
    "no_db_save": False,
    "nodelist": [],
    "oneshot": False,
    "out": [],
    "planner": "",
    "plotters": [],
    "planners": [],
    "problem": "",
    "quiet": 0,
    "timeout": 5,
    "timeout_offset": 10,
    "user_mail": None,
    "verbose": 0,
}


def merge_configs(cli_config: dict, file_config: dict, default_config: dict) -> dict:
    config = default_config.copy()
    config.update(file_config)

    for k, v in cli_config.items():
        if isinstance(v, (list, tuple)):
            if list(v) != list(default_config[k]):
                config[k] = v
        elif isinstance(v, int) and not isinstance(v, bool):
            config[k] = v
        elif v is not None and v != default_config[k]:
            config[k] = v

    return config


def merge_running_modes(anytime: bool, oneshot: bool) -> List[RunningMode]:
    if anytime and oneshot:
        return [RunningMode.ANYTIME, RunningMode.ONESHOT]
    if anytime:
        return [RunningMode.ANYTIME]
    if oneshot:
        return [RunningMode.ONESHOT]
    return [RunningMode.ANYTIME, RunningMode.ONESHOT]


def yaml_config(path: Optional[Path], name: str) -> dict:
    config = load_config("cli", path)
    if name in config:
        return config[name] or {}
    return {}


# ============================================================================ #
#                                    Options                                   #
# ============================================================================ #


pass_context = click.make_pass_decorator(CliContext, ensure=True)


anytime_option = click.option(
    "--anytime",
    is_flag=True,
    help="Perform anytime solving method only.",
)
config_option = click.option(
    "-c",
    "--config",
    type=click.Path(exists=True),
    help="Path to a configuration file.",
)
db_only_option = click.option(
    "--db-only",
    is_flag=True,
    help="Only use the database for results.",
)
db_path_option = click.option(
    "--db-path",
    type=str,
    help="Path to the SQLite database file.",
)
domains_filter = click.option(
    "-d",
    "--domains",
    type=str,
    multiple=True,
    help="A list of regex filters on domain names. A domain name is of the form DOMAIN:UID.",
)
jobs_option = click.option(
    "-j",
    "--jobs",
    type=int,
    help=f"Number of CPUs to use for parallel computation, \
if negative (n_cpus + 1 + jobs) are used. Default to {DEFAULT_CONFIG['jobs']}.",
)
latex_option = click.option(
    "--latex",
    is_flag=True,
    help="Generate LaTeX code of the result.",
)
logs_path_option = click.option(
    "--logs-path",
    type=str,
    help="Path to the logs directory.",
)
memout_option = click.option(
    "-m",
    "--memout",
    type=int,
    help="Memout for planners in bytes. Default to 4GB.",
)
metrics_filter = click.option(
    "-M",
    "--metrics",
    type=str,
    multiple=True,
    help="A list of regex filters on metric names.",
)
no_db_load_option = click.option(
    "--no-db-load",
    is_flag=True,
    help="Do not use the database for results loading.",
)
no_db_save_option = click.option(
    "--no-db-save",
    is_flag=True,
    help="Do not use the database for results saving.",
)
oneshot_option = click.option(
    "--oneshot",
    is_flag=True,
    help="Perform oneshot solving method only.",
)
out_option = click.option(
    "-o",
    "--out",
    multiple=True,
    type=click.File("w"),
    help="Output files. Default to stdout.",
)
planners_filter = click.option(
    "-p",
    "--planners",
    type=str,
    multiple=True,
    help="A list of regex filters on planner names.",
)
plotters_filter = click.option(
    "-P",
    "--plotters",
    type=str,
    multiple=True,
    help="A list of regex filters on plotter names.",
)
quiet_option = click.option(
    "-q",
    "--quiet",
    count=True,
    help="Decrease verbosity.",
)
timeout_option = click.option(
    "-t",
    "--timeout",
    type=int,
    help=f"Timeout for planners in seconds. Default to {DEFAULT_CONFIG['timeout']}s.",
)
timeout_offset_option = click.option(
    "--timeout-offset",
    type=int,
    help=f"Additional seconds on timeout for planner to timeout by themselves.\
        Default to {DEFAULT_CONFIG['timeout_offset']}s.",
)
verbose_option = click.option(
    "-v",
    "--verbose",
    count=True,
    help="Increase verbosity.",
)


# ============================================================================ #
#                                     Main                                     #
# ============================================================================ #


@click.group()
@verbose_option
@quiet_option
@out_option
@logs_path_option
@db_path_option
@config_option
@pass_context
def cli(ctx: CliContext, verbose, quiet, out, logs_path, db_path, config):
    update_context(ctx, verbose, quiet, out, logs_path, db_path, config)


def update_context(ctx, verbose, quiet, out, logs_path, db_path, config):
    ctx.verbosity += verbose - quiet
    ctx.out.extend(out)
    ctx.config = config
    TyrPaths().logs = logs_path or TyrPaths().logs
    TyrPaths().db = db_path or TyrPaths().db


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
@logs_path_option
@db_path_option
@config_option
@timeout_option
@timeout_offset_option
@memout_option
@jobs_option
@planners_filter
@domains_filter
@anytime_option
@oneshot_option
@db_only_option
@no_db_load_option
@no_db_save_option
@pass_context
def cli_bench(
    ctx: CliContext,
    verbose: int,
    quiet: int,
    out,
    logs_path: str,
    db_path: str,
    config,
    timeout: int,
    timeout_offset: int,
    memout: int,
    jobs: int,
    planners: List[str],
    domains: List[str],
    anytime: bool,
    oneshot: bool,
    db_only: bool,
    no_db_load: bool,
    no_db_save: bool,
):
    config = config or ctx.config
    cli_config = {
        "verbose": verbose,
        "quiet": quiet,
        "out": out,
        "logs_path": logs_path,
        "db_path": db_path,
        "timeout": timeout,
        "timeout_offset": timeout_offset,
        "memout": memout,
        "jobs": jobs,
        "planners": planners,
        "domains": domains,
        "anytime": anytime,
        "oneshot": oneshot,
        "db_only": db_only,
        "no_db_load": no_db_load,
        "no_db_save": no_db_save,
    }
    conf = merge_configs(cli_config, yaml_config(config, "bench"), DEFAULT_CONFIG)
    update_context(
        ctx,
        conf["verbose"],
        conf["quiet"],
        conf["out"],
        conf["logs_path"],
        conf["db_path"],
        config,
    )

    running_modes = merge_running_modes(conf["anytime"], conf["oneshot"])
    if conf["db_only"] and conf["no_db_load"]:
        raise click.BadOptionUsage(
            "--db-only --no-db-load",
            "Cannot use both --db-only and --no-db-load.",
        )

    solve_config = SolveConfig(
        conf["jobs"],
        conf["memout"],
        conf["timeout"],
        conf["timeout_offset"],
        conf["db_only"],
        conf["no_db_load"],
        conf["no_db_save"],
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
@logs_path_option
@db_path_option
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
    logs_path: str,
    db_path: str,
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
        "logs_path": logs_path,
        "db_path": db_path,
        "timeout": timeout,
        "memout": memout,
        "planners": planners,
        "domains": domains,
        "plotters": plotters,
        "latex": latex,
    }
    conf = merge_configs(cli_config, yaml_config(config, "plot"), DEFAULT_CONFIG)
    update_context(
        ctx,
        conf["verbose"],
        conf["quiet"],
        conf["out"],
        conf["logs_path"],
        conf["db_path"],
        config,
    )

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
#                                     Slurm                                    #
# ============================================================================ #


@cli.command(
    "slurm",
    help="Create the slurm script to run the resolution.",
)
@verbose_option
@quiet_option
@out_option
@logs_path_option
@db_path_option
@config_option
@timeout_option
@timeout_offset_option
@memout_option
@planners_filter
@domains_filter
@anytime_option
@oneshot_option
@click.option(
    "--user-mail",
    type=str,
    help="Email to send the notifications.",
)
@click.option(
    "--nodelist",
    type=str,
    multiple=True,
    help="The list of nodes to use on the cluster.",
)
@pass_context
def cli_slurm(
    ctx: CliContext,
    verbose: int,
    quiet: int,
    out,
    logs_path: str,
    db_path: str,
    config,
    timeout: int,
    timeout_offset: int,
    memout: int,
    planners: List[str],
    domains: List[str],
    anytime: bool,
    oneshot: bool,
    user_mail: str,
    nodelist: List[str],
):
    config = config or ctx.config
    cli_config = {
        "verbose": verbose,
        "quiet": quiet,
        "out": out,
        "logs_path": logs_path,
        "db_path": db_path,
        "timeout": timeout,
        "timeout_offset": timeout_offset,
        "memout": memout,
        "planners": planners,
        "domains": domains,
        "anytime": anytime,
        "oneshot": oneshot,
        "user_mail": user_mail,
        "nodelist": nodelist,
    }
    conf = merge_configs(cli_config, yaml_config(config, "slurm"), DEFAULT_CONFIG)
    update_context(
        ctx,
        conf["verbose"],
        conf["quiet"],
        conf["out"],
        conf["logs_path"],
        conf["db_path"],
        config,
    )

    running_modes = merge_running_modes(conf["anytime"], conf["oneshot"])

    solve_config = SolveConfig(
        jobs=1,
        memout=conf["memout"],
        timeout=conf["timeout"],
        timeout_offset=conf["timeout_offset"],
        db_only=False,
        no_db_load=False,
        no_db_save=False,
    )

    run_slurm(
        ctx,
        solve_config,
        conf["planners"],
        conf["domains"],
        running_modes,
        conf["user_mail"],
        conf["nodelist"],
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
@logs_path_option
@db_path_option
@config_option
@click.argument("planner", type=str, required=False)
@click.argument("problem", type=str, required=False)
@timeout_option
@timeout_offset_option
@memout_option
@click.option(
    "--fs",
    "--first-solution",
    is_flag=True,
    help="Stop the search after the first found solution.",
)
@no_db_save_option
@pass_context
def cli_solve(
    ctx: CliContext,
    verbose,
    quiet: int,
    out,
    logs_path: str,
    db_path: str,
    config,
    planner: str,
    problem: str,
    timeout: int,
    timeout_offset: int,
    memout: int,
    fs: bool,
    no_db_save: bool,
):
    config = config or ctx.config
    cli_config = {
        "verbose": verbose,
        "quiet": quiet,
        "out": out,
        "logs_path": logs_path,
        "db_path": db_path,
        "planner": planner,
        "problem": problem,
        "timeout": timeout,
        "timeout_offset": timeout_offset,
        "memout": memout,
        "fs": fs,
        "no_db_save": no_db_save,
    }
    conf = merge_configs(cli_config, yaml_config(config, "solve"), DEFAULT_CONFIG)

    if conf["planner"] == "":
        raise click.BadArgumentUsage("Missing argument 'PLANNER'.")
    if conf["problem"] == "":
        raise click.BadArgumentUsage("Missing argument 'PROBLEM'.")

    update_context(
        ctx,
        conf["verbose"],
        conf["quiet"],
        conf["out"],
        conf["logs_path"],
        conf["db_path"],
        config,
    )

    running_mode = RunningMode.ONESHOT if conf["fs"] else RunningMode.ANYTIME

    solve_config = SolveConfig(
        jobs=1,
        memout=conf["memout"],
        timeout=conf["timeout"],
        timeout_offset=conf["timeout_offset"],
        db_only=False,
        no_db_load=True,
        no_db_save=conf["no_db_save"],
    )
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
@logs_path_option
@db_path_option
@config_option
@timeout_option
@memout_option
@planners_filter
@domains_filter
@metrics_filter
@latex_option
@click.option(
    "--latex-array-stretch",
    type=float,
    help="Stretch the LaTeX table vertically. "
    f"Default: {DEFAULT_CONFIG['latex_array_stretch']}",
)
@click.option(
    "--latex-caption",
    type=str,
    help=f"Caption for the LaTeX table. Default: {DEFAULT_CONFIG['latex_caption']}",
)
@click.option(
    "--latex-font-size",
    type=str,
    help="Font size for the LaTeX table. "
    f"Default: {DEFAULT_CONFIG['latex_font_size']}",
)
@click.option(
    "--latex-horizontal-space",
    type=float,
    help="Horizontal space between columns for the LaTeX table in cm. "
    f"Default: {DEFAULT_CONFIG['latex_horizontal_space']}cm",
)
@click.option(
    "--latex-pos",
    type=str,
    help=f"Position of the LaTeX table. Default: {DEFAULT_CONFIG['latex_pos']}",
)
@click.option(
    "--latex-star",
    is_flag=True,
    help="Use a table* environment in LaTeX. Default: table.",
)
@pass_context
def cli_table(
    ctx: CliContext,
    verbose: int,
    quiet: int,
    out,
    logs_path: str,
    db_path: str,
    config,
    timeout: int,
    memout: int,
    planners: List[str],
    domains: List[str],
    metrics: List[str],
    latex: bool,
    latex_array_stretch: float,
    latex_caption: str,
    latex_font_size: str,
    latex_horizontal_space: float,
    latex_pos: str,
    latex_star: bool,
):
    config = config or ctx.config
    cli_config = {
        "verbose": verbose,
        "quiet": quiet,
        "out": out,
        "logs_path": logs_path,
        "db_path": db_path,
        "timeout": timeout,
        "memout": memout,
        "planners": planners,
        "domains": domains,
        "metrics": metrics,
        "latex": latex,
        "latex_array_stretch": latex_array_stretch,
        "latex_caption": latex_caption,
        "latex_font_size": latex_font_size,
        "latex_horizontal_space": latex_horizontal_space,
        "latex_pos": latex_pos,
        "latex_star": latex_star,
    }
    conf = merge_configs(cli_config, yaml_config(config, "table"), DEFAULT_CONFIG)
    update_context(
        ctx,
        conf["verbose"],
        conf["quiet"],
        conf["out"],
        conf["logs_path"],
        conf["db_path"],
        config,
    )

    run_table(
        ctx,
        conf["timeout"],
        conf["memout"],
        conf["planners"],
        conf["domains"],
        conf["metrics"],
        conf["latex"],
        conf["latex_array_stretch"],
        conf["latex_caption"],
        conf["latex_font_size"],
        conf["latex_horizontal_space"],
        conf["latex_pos"],
        conf["latex_star"],
    )


if __name__ == "__main__":
    cli()  # pylint: disable = no-value-for-parameter
