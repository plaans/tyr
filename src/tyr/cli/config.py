from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, TextIO


@dataclass
class CliContext:
    """Stores the shared arguments of the CLI."""

    out: List[TextIO] = field(default_factory=list)
    verbosity: int = 0
    config: Optional[Path] = None


__all__ = ["CliContext"]
