import re
from typing import List, Optional, TextIO, Tuple, cast

import unified_planning.shortcuts as upf
from unified_planning.exceptions import UPNoRequestedEngineAvailableException

from tyr.cli.config import CliContext
from tyr.planners.loader import register_all_planners
from tyr.planners.scanner import get_all_planner_configs


def run_list_planners(
    ctx: CliContext,
    verbose: bool = False,
    filter_pattern: Optional[str] = None,
):
    """List all available planners with their configurations.

    Args:
        ctx (CliContext): The CLI execution context.
        verbose (bool): Whether to show detailed planner information.
        filter_pattern (str): Optional regex pattern to filter planner names.
    """
    # Register all planners to ensure they are loaded
    register_all_planners()

    # Silence UPF credits output
    upf.get_environment().credits_stream = None

    # Get all planner configurations
    planner_configs = get_all_planner_configs()

    # Filter planners if pattern is provided
    if filter_pattern:
        pattern = re.compile(filter_pattern, re.IGNORECASE)
        planner_configs = [
            config for config in planner_configs if pattern.search(config.name)
        ]

    # Sort planners by name
    planner_configs.sort(key=lambda x: x.name)

    # Get output streams (default to stdout if none specified)
    output_streams: List[Optional[TextIO]] = (
        cast(List[Optional[TextIO]], ctx.out) if ctx.out else [None]
    )

    for stream in output_streams:
        _write_planners_list(planner_configs, verbose, stream)


def _write_planners_list(
    planner_configs: List, verbose: bool, stream: Optional[TextIO] = None
):
    """Write the planners list to the specified stream."""
    if not planner_configs:
        print("No planners found.", file=stream)
        return

    if verbose:
        _write_verbose_list(planner_configs, stream)
    else:
        _write_compact_list(planner_configs, stream)


def _write_compact_list(planner_configs: List, stream: Optional[TextIO] = None):
    """Write a compact list of planners."""
    print(f"Found {len(planner_configs)} planner(s):", file=stream)
    print("", file=stream)

    # Calculate column widths
    max_name_width = max(len(config.name) for config in planner_configs)
    max_name_width = max(max_name_width, len("PLANNER"))

    # Print header
    print(f"{'PLANNER':<{max_name_width}}  {'STATUS':<13}  UPF ENGINE", file=stream)
    print(f"{'-' * max_name_width}  {'-' * 13}  {'-' * 50}", file=stream)

    # Print planner rows
    for config in planner_configs:
        oneshot_available, anytime_available, engine_info = _check_planner_availability(
            config
        )

        if oneshot_available or anytime_available:
            status = "Available"
        else:
            status = "Not Available"

        engine = engine_info or "N/A"
        print(f"{config.name:<{max_name_width}}  {status:<13}  {engine}", file=stream)


def _write_verbose_list(planner_configs: List, stream: Optional[TextIO] = None):
    """Write a detailed list of planners."""
    print(f"Found {len(planner_configs)} planner(s):", file=stream)
    print("", file=stream)

    for i, config in enumerate(planner_configs):
        if i > 0:
            print("", file=stream)

        oneshot_available, anytime_available, engine_info = _check_planner_availability(
            config
        )

        print(f"Planner: {config.name}", file=stream)
        print(f"  UPF Engine: {engine_info or 'None'}", file=stream)

        # Show availability status
        print("  Availability:", file=stream)
        oneshot_name = config.oneshot_name or config.name
        anytime_name = config.anytime_name or config.name

        if oneshot_name == "unsupported-mode":
            print("    Oneshot: Unsupported", file=stream)
        else:
            status = "Available" if oneshot_available else "Not Available"
            print(f"    Oneshot ({oneshot_name}): {status}", file=stream)

        if anytime_name == "unsupported-mode":
            print("    Anytime: Unsupported", file=stream)
        else:
            status = "Available" if anytime_available else "Not Available"
            print(f"    Anytime ({anytime_name}): {status}", file=stream)

        if config.env:
            print("  Environment variables:", file=stream)
            for key, value in config.env.items():
                print(f"    {key}: {value}", file=stream)

        if config.upf_params:
            print("  UPF parameters:", file=stream)
            for key, value in config.upf_params.items():
                print(f"    {key}: {value}", file=stream)

        if config.problems:
            print("  Problem-specific configurations:", file=stream)
            for domain, version in config.problems.items():
                print(f"    {domain}: {version}", file=stream)


def _check_planner_availability(config) -> Tuple[bool, bool, Optional[str]]:
    """Check availability of a planner for both oneshot and anytime modes.

    Args:
        config: PlannerConfig object

    Returns:
        Tuple of (oneshot_available, anytime_available, engine_info)
    """
    oneshot_available = False
    anytime_available = False
    engine_info = None

    # Check oneshot mode if not marked as unsupported
    oneshot_name = config.oneshot_name or config.name
    if oneshot_name != "unsupported-mode":
        try:
            with upf.OneshotPlanner(name=oneshot_name) as planner:
                oneshot_available = True
                if engine_info is None:
                    engine_info = (
                        f"{planner.__class__.__module__}.{planner.__class__.__name__}"
                    )
        except UPNoRequestedEngineAvailableException:
            pass
        except Exception:  # pylint: disable=broad-exception-caught  # nosec: B110
            # Handle other exceptions silently
            pass

    # Check anytime mode if not marked as unsupported
    anytime_name = config.anytime_name or config.name
    if anytime_name != "unsupported-mode":
        try:
            with upf.AnytimePlanner(name=anytime_name) as planner:
                anytime_available = True
                if engine_info is None:
                    engine_info = (
                        f"{planner.__class__.__module__}.{planner.__class__.__name__}"
                    )
        except UPNoRequestedEngineAvailableException:
            pass
        except Exception:  # pylint: disable=broad-exception-caught  # nosec: B110
            # Handle other exceptions silently
            pass

    # If we have upf_engine in config, prefer that for display
    if config.upf_engine:
        engine_info = config.upf_engine

    return oneshot_available, anytime_available, engine_info


__all__ = ["run_list_planners"]
