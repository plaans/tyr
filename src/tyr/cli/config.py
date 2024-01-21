from dataclasses import dataclass
from typing import Optional, TextIO


@dataclass
class CliContext:
    """Stores the shared arguments of the CLI."""

    out: Optional[TextIO] = None
    verbosity: int = 0
