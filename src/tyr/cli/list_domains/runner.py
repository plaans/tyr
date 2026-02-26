import re
from typing import List, Optional, TextIO, cast

from tyr.cli.config import CliContext
from tyr.problems.scanner import get_all_domains


def run_list_domains(
    ctx: CliContext,
    verbose: bool = False,
    filter_pattern: Optional[str] = None,
):
    """List all available domains with their configurations.

    Args:
        ctx (CliContext): The CLI execution context.
        verbose (bool): Whether to show detailed domain information.
        filter_pattern (str): Optional regex pattern to filter domain names.
    """
    # Get all domains
    domains = get_all_domains()

    # Filter domains if pattern is provided
    if filter_pattern:
        pattern = re.compile(filter_pattern, re.IGNORECASE)
        domains = [domain for domain in domains if pattern.search(domain.name)]

    # Sort domains by name
    domains.sort(key=lambda x: x.name)

    # Get output streams (default to stdout if none specified)
    output_streams: List[Optional[TextIO]] = (
        cast(List[Optional[TextIO]], ctx.out) if ctx.out else [None]
    )

    for stream in output_streams:
        _write_domains_list(domains, verbose, stream)


def _write_domains_list(domains: List, verbose: bool, stream: Optional[TextIO] = None):
    """Write the domains list to the specified stream."""
    if not domains:
        print("No domains found.", file=stream)
        return

    if verbose:
        _write_verbose_list(domains, stream)
    else:
        _write_compact_list(domains, stream)


def _write_compact_list(domains: List, stream: Optional[TextIO] = None):
    """Write a compact list of domains."""
    print(f"Found {len(domains)} domain(s):", file=stream)
    print("", file=stream)

    # Calculate column widths
    max_name_width = max(len(domain.name) for domain in domains)
    max_name_width = max(max_name_width, len("DOMAIN"))

    # Print header
    print(
        f"{'DOMAIN':<{max_name_width}}  {'NUM PROBLEMS':<15}  VERSIONS", file=stream
    )
    print(f"{'-' * max_name_width}  {'-' * 15}  {'-' * 50}", file=stream)

    # Print domain rows
    for domain in domains:
        num_problems = _get_num_problems_safe(domain)
        versions = ", ".join(domain.get_versions())

        print(
            f"{domain.name:<{max_name_width}}  {num_problems:<15}  {versions}",
            file=stream,
        )


def _write_verbose_list(domains: List, stream: Optional[TextIO] = None):
    """Write a detailed list of domains."""
    print(f"Found {len(domains)} domain(s):", file=stream)
    print("", file=stream)

    for i, domain in enumerate(domains):
        if i > 0:
            print("", file=stream)

        print(f"Domain: {domain.name}", file=stream)

        # Show number of problems
        num_problems = _get_num_problems_safe(domain)
        print(f"  Number of problems: {num_problems}", file=stream)

        # Show versions
        versions = domain.get_versions()
        if versions:
            print("  Available versions:", file=stream)
            for version in versions:
                print(f"    - {version}", file=stream)
        else:
            print("  Available versions: None", file=stream)


def _get_num_problems_safe(domain) -> str:
    """Safely get the number of problems for a domain.

    Args:
        domain: AbstractDomain object

    Returns:
        String representation of the number of problems or "Unknown"
    """
    try:
        num_problems = domain.get_num_problems()
        return str(num_problems)
    except (NotImplementedError, Exception):  # pylint: disable=broad-exception-caught
        return "Unknown"


__all__ = ["run_list_domains"]
