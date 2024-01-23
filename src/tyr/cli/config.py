from dataclasses import dataclass, field
from typing import List, TextIO


@dataclass
class CliContext:
    """Stores the shared arguments of the CLI."""

    out: List[TextIO] = field(default_factory=list)
    verbosity: int = 0
