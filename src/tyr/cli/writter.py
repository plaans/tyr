import os
import platform
import shutil
import sys
import time
from pathlib import Path
from typing import List, Optional, TextIO, Union

from tyr.cli.collector import CollectionResult
from tyr.configuration.loader import get_config_file
from tyr.core.paths import TyrPaths
from tyr.planners.model.config import SolveConfig


def _should_do_markup(file: TextIO) -> bool:
    if os.environ.get("PY_COLORS") == "1":
        return True
    if os.environ.get("PY_COLORS") == "0":
        return False
    if "NO_COLOR" in os.environ:
        return False
    if "FORCE_COLOR" in os.environ:
        return True
    return (
        hasattr(file, "isatty") and file.isatty() and os.environ.get("TERM") != "dumb"
    )


class Writter:
    """Utility class to write content on an output textio."""

    _esctable = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "purple": 35,
        "cyan": 36,
        "white": 37,
        "Black": 40,
        "Red": 41,
        "Green": 42,
        "Yellow": 43,
        "Blue": 44,
        "Purple": 45,
        "Cyan": 46,
        "White": 47,
        "bold": 1,
        "light": 2,
        "blink": 5,
        "invert": 7,
    }

    def __init__(
        self,
        solve_config: SolveConfig,
        out: Union[Optional[TextIO], List[TextIO]] = None,
        verbosity: int = 0,
        config: Optional[Path] = None,
    ) -> None:
        """
        Args:
            out (Union[Optional[TextIO], List[TextIO]], optional): The output where to write.
                It can be a list of outputs to write in multiple places. Defaults to stdout.
            verbosity (int, optional): Verbosity level. Defaults to 0.
            config (Optional[Path], optional): The configuration file used.
        """
        if out is None or out == [] or out == tuple():
            out = sys.stdout
        if not isinstance(out, (list, tuple)):
            out = [out]
        self._out = list(out)
        self._verbosity = verbosity
        self._config = get_config_file("cli", config)
        self._solve_config = solve_config
        self._crt_line = ""
        self._fullwidth = shutil.get_terminal_size(fallback=(80, 24))[0]
        self._starttime = 0

    # ============================================================================ #
    #                                    Getters                                   #
    # ============================================================================ #

    @property
    def verbosity(self) -> int:
        """
        Returns:
            int: The verbosity level to use.
        """
        return self._verbosity

    @property
    def verbose(self) -> bool:
        """
        Returns:
            bool: Whether verbose mode is active.
        """
        return self.verbosity > 0

    @property
    def quiet(self) -> bool:
        """
        Returns:
            bool: Whether quiet mode is active.
        """
        return self.verbosity < 0

    @property
    def current_line_width(self) -> int:
        """
        Returns:
            int: Length of the current line.
        """
        return len(self._crt_line)

    # ============================================================================ #
    #                                  Print stuff                                 #
    # ============================================================================ #

    def write(self, text: str, flush: bool = False, **markup: bool) -> None:
        """Writes the given text with optional effects.

        Args:
            text (str): The text to write.
            flush (bool, optional): Whether to flush the output. Defaults to False.
            markup (Dict[str, bool], optional): The effects to apply to the text.
        """
        if text:
            crt_line = text.rsplit("\n", 1)[-1]
            if "\n" in text:
                self._crt_line = crt_line
            else:
                self._crt_line += crt_line

            text = self.markup(text, **markup)

            for out in self._out:
                if not _should_do_markup(out):
                    text = self.unmarkup(text)
                out.write(text)

            if flush:
                self.flush()

    def rewrite(self, text: str = "", erase: bool = False, **markup: bool) -> None:
        """Writes on top of the previous text.

        Args:
            text (str, optional): The text to write. Defaults to "".
            erase (bool, optional): Whether to erase the full previous line. Defaults to False.
            markup (Dict[str, bool], optional): The effects to apply to the text.
        """
        self._crt_line = ""
        fill = (" " * (self._fullwidth - len(text))) if erase else ""
        self.write(f"\r{text}{fill}", **markup)

    def flush(self) -> None:
        """Flushes the output."""
        for out in self._out:
            out.flush()

    def line(self, text: str = "", **markup: bool) -> None:
        """Writes the given text and finishes with a new line.

        Args:
            text (str, optional): The text to write. Defaults to "".
            markup (Dict[str, bool], optional): The effects to apply to the text.
        """
        self.write(text, **markup)
        self.write("\n")

    def separator(
        self,
        sepchar: str,
        title: Optional[str] = None,
        fullwidth: Optional[int] = None,
        **markup: bool,
    ):
        """Writes a seperator with an optional centered title.

        Args:
            sepchar (str): The character to use for the separator.
            title (Optional[str], optional): The centered title to write. Defaults to None.
            fullwidth (Optional[int], optional): The width to use. Defaults to terminal width.
            markup (Dict[str, bool], optional): The effects to apply to the title.
        """
        if fullwidth is None:
            fullwidth = self._fullwidth

        if title is None:
            line = sepchar * (fullwidth // len(sepchar))
        else:
            n = max((fullwidth - len(title) - 2) // (2 * len(sepchar)), 1)
            fill = sepchar * n
            line = f"{fill} {title} {fill}"

        if len(line) + len(sepchar.rstrip()) <= fullwidth:
            line += sepchar.rstrip()

        self.line(line, **markup)

    # ============================================================================ #
    #                                    Report                                    #
    # ============================================================================ #

    def report_collecting(self):
        """Reports the beginning of a collection process."""
        if not self.quiet:
            self.write("collecting...", flush=True, bold=True)

    def report_collected(self, result: CollectionResult, name: str):
        """Reports the result of a collection process."""
        if self.quiet:
            return

        total = result.total
        selected = len(result.selected)
        deselected = len(result.deselected)
        skipped = len(result.skipped)

        line = f"collected {total} {name}" + ("" if total <= 1 else "s")
        if deselected:
            line += f" / {deselected} deselected"
        if skipped:
            line += f" / {skipped} skipped"
        if total > selected:
            line += f" / {selected} selected"

        self.line(line, bold=True)

    def report_solve_config(self):
        """Prints a report about the configuration being used for the resolution."""
        if self.quiet:
            return

        # Database
        db_status = (
            "disabled"
            if self._solve_config.no_db_load and self._solve_config.no_db_save
            else (
                "load only"
                if self._solve_config.no_db_save
                else (
                    "save only"
                    if self._solve_config.no_db_load
                    else "unique source"
                    if self._solve_config.db_only
                    else "enabled"
                )
            )
        )
        self.line(f"database: {TyrPaths().db.resolve().absolute()} -- {db_status}")

        # Timeout
        timeout = self.format_seconds(self._solve_config.timeout)
        offset = self.format_seconds(self._solve_config.timeout_offset)
        msg = f"timeout: {timeout} ± {offset}"
        num_bytes = self._solve_config.memout * 1.0

        # Memout
        msg += f" -- memout: {int(num_bytes)} Bytes"
        for unit in ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
            if num_bytes < 1024:
                msg += f" ({num_bytes:.2f} {unit})"
                break
            num_bytes /= 1024

        # Parallel
        msg += f" -- jobs: {self._solve_config.jobs}"
        self.line(msg)

    # ============================================================================ #
    #                                    Session                                   #
    # ============================================================================ #

    def session_name(self) -> str:
        """The name of the sessions."""
        raise NotImplementedError

    def session_starts(self):
        """Prints information about the starting session."""
        self._starttime = time.time()
        if self.quiet:
            return

        self.separator("=", f"Tyr {self.session_name()} session starts", bold=True)
        self.line(f"start at {time.strftime('%Y-%m-%d %H:%M:%S')} on {platform.node()}")
        msg = f"platform {sys.platform} -- Python {platform.python_version()} -- {sys.executable}"
        self.line(msg)
        self.line(f"rootdir: {os.getcwd()} -- verbosity: {self.verbosity}")
        self.line(f"config: {self._config.resolve().absolute()}")
        self.line(f"logs: {TyrPaths().logs.resolve().absolute()}")
        self.report_solve_config()
        self.report_collecting()

    # ============================================================================ #
    #                                  Formatting                                  #
    # ============================================================================ #

    def format_seconds(self, seconds: int) -> str:
        """Formats the given number of seconds into a more readable format.

        Args:
            seconds (int): The seconds to format.

        Returns:
            str: The readable string.
        """
        msg = f"{seconds}s"
        if seconds >= 60:
            hours = seconds // 3600
            minutes = (seconds // 60) % 60
            seconds = seconds % 60
            if hours > 0:
                msg += f" ({hours:0>2}:{minutes:0>2}:{seconds:0>2})"
            else:
                msg += f" ({minutes:0>2}:{seconds:0>2})"
        return msg

    def markup(self, text: str, **markup: bool) -> str:
        """Adds tokens to customize the given text.

        Args:
            text (str): The text to customize.
            markup (Dict[str, bool], optional): The effects to apply to the text.

        Raises:
            ValueError: When a markup name is unknown.

        Returns:
            str: The customized text.
        """
        for name in markup:
            if name not in self._esctable:
                raise ValueError(f"Unknown markup: {name!r}")
        esc = [self._esctable[name] for name, on in markup.items() if on]
        if esc:
            text = "".join(f"\x1b[{cod}m" for cod in esc) + text + "\x1b[0m"
        return text

    def unmarkup(self, text: str) -> str:
        """Removes the customization tokens of the given text.

        Args:
            text (str): The text to unwrap.

        Returns:
            str: The unwrapped text.
        """
        for cod in self._esctable.values():
            text = text.replace(f"\x1b[{cod}m", "")
        return text.replace("\x1b[0m", "")


__all__ = ["Writter"]
