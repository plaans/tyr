from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, Generator, List, Optional, Set, TextIO, Tuple, Union

from tyr.cli.collector import CollectionResult
from tyr.cli.writter import Writter
from tyr.configuration.loader import load_config
from tyr.metrics.metric import Metric
from tyr.planners.model.config import SolveConfig
from tyr.planners.model.planner import Planner
from tyr.planners.model.result import PlannerResult, PlannerResultStatus
from tyr.problems.model.domain import AbstractDomain
from tyr.problems.model.instance import ProblemInstance


class Adjust(Enum):
    """Enumeration of the possible horizontal adjustments for a cell value."""

    CENTER = auto()
    LEFT = auto()
    RIGHT = auto()


class Sep(Enum):
    """Enumeration of the possible separators for a table."""

    SIMPLE = auto()
    DOUBLE = auto()

    def fmt(self, latex: bool) -> str:
        """Returns the string representation of the separator."""
        if self is Sep.SIMPLE:
            return "&" if latex else "│"
        if self is Sep.DOUBLE:
            return "& &" if latex else "║"
        raise NotImplementedError(f"{self} is not supported to print a separator")

    def __str__(self) -> str:
        return self.fmt(False)


@dataclass
class Cell:
    """Data class representing a cell in a table."""

    value: str
    adjust: Adjust
    h_span: int = 1
    v_span: int = 1
    length: int = -1

    def __post_init__(self):
        if self.length == -1:
            self.length = len(self.value)

    def fmt(self, latex: bool) -> str:
        """Returns the string representation of the cell."""
        if latex:
            a = (
                "c"
                if self.adjust == Adjust.CENTER
                else "l" if self.adjust == Adjust.LEFT else "r"
            )
            return f"\\multicolumn{{{self.h_span}}}{{{a}}}{{{self.value.strip()}}}"
        if self.adjust == Adjust.CENTER:
            return self.value.center(self.length)
        if self.adjust == Adjust.LEFT:
            return self.value.ljust(self.length)
        if self.adjust == Adjust.RIGHT:
            return self.value.rjust(self.length)
        raise NotImplementedError(f"{self.adjust} is not supported to print a cell")

    def __str__(self) -> str:
        return self.fmt(False)


@dataclass
class CellRow:
    """Data class representing a row in a table."""

    row: List[Union[Cell, Sep]]

    @property
    def cells(self) -> Generator[Cell, None, None]:
        """Yields the cells in the row."""
        yield from (cell for cell in self.row if isinstance(cell, Cell))

    def append(self, item: Union[Cell, Sep]):
        """Appends an item to the row."""
        self.row.append(item)

    def pop(self):
        """Pops the last item from the row."""
        self.row.pop()

    def column_of(self, cell: Cell):
        """Returns the column of a cell in the row."""
        col = 0
        for item in self.cells:
            if item is cell:
                return col
            col += item.h_span
        raise ValueError(f"{cell} is not in the row.")

    def index(self, item: Union[Cell, Sep], start: int = 0):
        """Returns the index of an item in the row."""
        return self.row.index(item, start)

    @property
    def num_columns(self) -> int:
        """Returns the number of columns in the row."""
        return sum(cell.h_span for cell in self.cells)

    def __iter__(self):
        return self.row.__iter__()

    def __getitem__(self, idx):
        return self.row[idx]

    def __len__(self):
        return len(self.row)


@dataclass
class CellTable:
    """Data class representing a table of cells."""

    rows: List[Union[CellRow, Sep]]

    @property
    def lines(self) -> Generator[CellRow, None, None]:
        """Yields the rows in the table."""
        yield from (line for line in self.rows if isinstance(line, CellRow))

    def append(self, item: Union[CellRow, Sep]):
        """Appends an item to the table."""
        self.rows.append(item)

    def pop(self):
        """Pops the last item from the table."""
        self.rows.pop()

    def __iter__(self):
        return self.rows.__iter__()

    def __getitem__(self, idx):
        return self.rows[idx]

    def __len__(self):
        return len(self.rows)


# pylint: disable = too-many-instance-attributes
class TableTerminalWritter(Writter):
    """Terminal writter for the analysis command."""

    # pylint: disable = too-many-arguments
    def __init__(
        self,
        solve_config: SolveConfig,
        out: Union[Optional[TextIO], List[TextIO]] = None,
        verbosity: int = 0,
        config: Optional[Path] = None,
        latex: bool = False,
        latex_array_stretch: float = 1.2,
        latex_caption: str = "",
        latex_font_size: str = "footnotesize",
        latex_horizontal_space: float = 0.35,
        latex_pos: str = "htb",
        latex_star: bool = False,
    ) -> None:
        super().__init__(solve_config, out, verbosity, config)
        self._results: List[PlannerResult] = []
        self._planners: List[Planner] = []
        self._problems: List[ProblemInstance] = []
        self._metrics: List[Metric] = []
        self._latex = latex
        self._latex_array_stretch = latex_array_stretch
        self._latex_caption = latex_caption
        self._latex_font_size = latex_font_size
        self._latex_horizontal_space = latex_horizontal_space
        self._latex_pos = latex_pos
        self._latex_star = latex_star

    # =============================== Manipulation =============================== #

    def set_results(self, results: List[PlannerResult]):
        """Modifies the stored results.

        Args:
            results (List[Optional[PlannerResult]]): The results to store.
        """
        self._results = PlannerResult.merge_all(results)

        if not self.quiet:
            total = len(self._results)
            msg = f"collected {total} result" + ("" if total <= 1 else "s")
            self.line(msg, bold=True)

    # ================================== Report ================================== #

    def report_collect(
        self,
        planners: CollectionResult[Planner],
        problems: CollectionResult[ProblemInstance],
        metrics: CollectionResult[Metric],
    ) -> None:
        """Prints a report about the collection of planners and problems.

        Args:
            planners (CollectionResult[Planner]): The collection result on planners.
            problems (CollectionResult[ProblemInstance]): The collection result on problems.
            metrics (CollectionResult[Metric]): The collection result on metrics.
        """
        self.rewrite("")
        self.report_collected(planners, "planner")
        self.report_collected(problems, "problem")
        self.report_collected(metrics, "metric")

        self._planners = sorted(planners.selected, key=lambda p: p.name)
        self._problems = sorted(problems.selected, key=lambda p: p.name)
        self._metrics = sorted(metrics.selected, key=lambda m: m.name)

    # ================================== Session ================================= #

    def session_name(self) -> str:
        return "table"

    # ================================== Analyse ================================= #

    # pylint: disable = too-many-branches, too-many-locals, eval-used
    # pylint: disable = too-many-statements, too-many-nested-blocks, fixme
    def analyse(self) -> None:
        """Prints a table of metrics based on results."""

        # Get the table configuration from the configuration file.
        conf = load_config("", self._config).get("table", {})
        default_ordering = "lambda x: (x == ' ', str(x))"
        conf_col_headers = conf.get("column_headers", [])
        if not conf_col_headers:
            conf_col_headers = [
                {"mapping": "lambda d, p, m: p.name"},
                {"mapping": "lambda d, p, m: m.abbrev()"},
            ]
        conf_row_headers = conf.get("row_headers", [])
        if not conf_row_headers:
            conf_row_headers = [
                {"mapping": "lambda d, p, m: d.name"},
            ]
        final_column = conf.get("final_column", None)
        final_row = conf.get("final_row", None)

        # Get all domains.
        domains = {p.domain for p in self._problems}

        # Get all headers.
        raw_col_headers: Dict[
            str, Union[Dict, Set[Tuple[AbstractDomain, Planner, Metric]]]
        ] = {}
        raw_row_headers: Dict[
            str, Union[Dict, Set[Tuple[AbstractDomain, Planner, Metric]]]
        ] = {}
        for d in domains:
            if d is None:
                continue
            for p in self._planners:
                for m in self._metrics:
                    crt_col_header = raw_col_headers
                    for i, conf_header in enumerate(conf_col_headers):
                        col_header = eval(conf_header["mapping"])(  # nosec: B307
                            d, p, m
                        )
                        if col_header not in crt_col_header:
                            if i == len(conf_col_headers) - 1:
                                crt_col_header[col_header] = {(d, p, m)}
                            else:
                                crt_col_header[col_header] = {}
                        elif i == len(conf_col_headers) - 1:
                            crt_col_header[col_header].add((d, p, m))  # type: ignore
                        crt_col_header = crt_col_header[col_header]  # type: ignore

                    crt_row_header = raw_row_headers
                    for i, conf_header in enumerate(conf_row_headers):
                        col_header = eval(conf_header["mapping"])(  # nosec: B307
                            d, p, m
                        )
                        if col_header not in crt_row_header:
                            if i == len(conf_row_headers) - 1:
                                crt_row_header[col_header] = {(d, p, m)}
                            else:
                                crt_row_header[col_header] = {}
                        elif i == len(conf_row_headers) - 1:
                            crt_row_header[col_header].add((d, p, m))  # type: ignore
                        crt_row_header = crt_row_header[col_header]  # type: ignore

        # Order the headers.
        def get_lvl(
            d: Union[Dict, Set],
            lvl: int,
            conf: List,
            crt_lvl: int = 0,
        ) -> Generator[Tuple[str, ...], None, None]:
            if isinstance(d, set):
                return
            ordering = conf[crt_lvl].get("ordering", default_ordering)
            for key in sorted(d.keys(), key=eval(ordering)):  # nosec: B307
                if lvl == 0:
                    yield (key,)
                else:
                    for val in get_lvl(d[key], lvl - 1, conf, crt_lvl + 1):
                        yield (key, *val)

        flat_col_headers = [
            list(get_lvl(raw_col_headers, i, conf_col_headers))
            for i in range(len(conf_col_headers))
        ]
        flat_row_headers = [
            list(get_lvl(raw_row_headers, i, conf_row_headers))
            for i in range(len(conf_row_headers))
        ]

        # Create the table.
        table = CellTable([Sep.DOUBLE])

        # Create the column headers.
        for i, col_headers in enumerate(flat_col_headers):
            v_span = len(flat_col_headers) * (1 if i == 0 else -1)
            head_empty = Cell("", Adjust.CENTER, len(flat_row_headers), v_span)
            tail_empty = Cell("", Adjust.CENTER, v_span=v_span)
            table.append(CellRow([Sep.DOUBLE, head_empty, Sep.DOUBLE]))
            # XXX: This assums that each "planner" has the same number of "metrics".
            col_modulo = int(len(col_headers) / len(flat_col_headers[-2]))
            for j, col_header in enumerate(col_headers):
                span = sum(
                    1
                    for col_subheader in flat_col_headers[-1]
                    if all(
                        col_header[k] == col_subheader[k]
                        for k in range(len(col_header))
                    )
                )
                table[-1].append(Cell(col_header[-1], Adjust.CENTER, span))
                if span == 1 and j % col_modulo < col_modulo - 1:
                    table[-1].append(Sep.SIMPLE)
                else:
                    table[-1].append(Sep.DOUBLE)
            if final_column is not None:
                if i == 0:
                    name = final_column["name"]
                    table[-1].append(Cell(name, Adjust.CENTER, v_span=v_span))
                else:
                    table[-1].append(tail_empty)
                table[-1].append(Sep.DOUBLE)
            table.append(Sep.DOUBLE)

        # Create the cells.
        col_values: List[List[float]] = [[] for _ in range(len(flat_col_headers[-1]))]
        for i, row_header in enumerate(flat_row_headers[-1]):
            row_values = []
            table.append(CellRow([Sep.DOUBLE]))
            for k, v in enumerate(row_header):
                is_first_header = (
                    i == 0
                    or flat_row_headers[-1][i - 1][: k + 1] != row_header[: k + 1]
                )
                to_print = v if is_first_header else ""
                v_span, j = 0, 0
                while (
                    i + j < len(flat_row_headers[-1])
                    and flat_row_headers[-1][i + j][: k + 1] == row_header[: k + 1]
                ):
                    v_span += 1
                    j += 1
                v_span = v_span * (1 if to_print else -1)
                table[-1].append(Cell(to_print, Adjust.RIGHT, v_span=v_span))
                table[-1].append(Sep.SIMPLE)
            table[-1].pop()
            table[-1].append(Sep.DOUBLE)

            for j, col_header in enumerate(flat_col_headers[-1]):
                crt_col_header: Set[Tuple] = raw_col_headers  # type: ignore
                for v in col_header:
                    crt_col_header = crt_col_header[v]  # type: ignore

                crt_row_header: Set[Tuple] = raw_row_headers  # type: ignore
                for v in row_header:
                    crt_row_header = crt_row_header[v]  # type: ignore

                candidates = crt_col_header.intersection(crt_row_header)  # type: ignore
                # Filter the candidates with unsupported results.
                candidates = {
                    candidate
                    for candidate in candidates
                    if all(
                        result.status != PlannerResultStatus.UNSUPPORTED
                        for result in self._results
                        if result.problem.domain == candidate[0]
                        and result.planner_name == candidate[1].name
                    )
                }

                if len(candidates) > 1:
                    raise ValueError(
                        f"Multiple candidates for {col_header} in {row_header}: {candidates}"
                    )
                if len(candidates) == 0:
                    value = "x"
                else:
                    d, p, m = candidates.pop()  # type: ignore
                    results = [
                        result
                        for result in self._results
                        if result.problem.domain == d and result.planner_name == p.name
                    ]
                    value = m.evaluate(results, self._results)
                    raw_value = m.evaluate_raw(results, self._results)
                    row_values.append(raw_value)
                    col_values[j].append(raw_value)

                table[-1].append(Cell(value, Adjust.RIGHT))
                # XXX: This assums that each "planner" has the same number of "metrics".
                if j % col_modulo < col_modulo - 1:
                    table[-1].append(Sep.SIMPLE)
                else:
                    table[-1].append(Sep.DOUBLE)
            if final_column is not None:
                final_row_val = eval(final_column["value"])(row_values)  # nosec: B307
                table[-1].append(Cell(f"{final_row_val:.2f}", Adjust.RIGHT))
                table[-1].append(Sep.DOUBLE)
            is_last_header = i == len(flat_row_headers[-1]) - 1 or any(
                flat_row_headers[-1][i + 1][k] != row_header[k]
                for k in range(len(row_header) - 1)
            )
            if is_last_header:
                table.append(Sep.DOUBLE)
            else:
                table.append(Sep.SIMPLE)
        table.pop()
        table.append(Sep.DOUBLE)
        if final_row is not None:
            table.append(CellRow([Sep.DOUBLE]))
            name = final_row["name"]
            table[-1].append(Cell(name, Adjust.CENTER, len(flat_row_headers[-1][-1])))
            table[-1].append(Sep.DOUBLE)
            for col_vals in col_values:
                final_row_val = eval(final_row["value"])(col_vals)  # nosec: B307
                table[-1].append(Cell(f"{final_row_val:.2f}", Adjust.RIGHT))
                table[-1].append(Sep.DOUBLE)
            if final_column is not None:
                table[-1].append(Cell("", Adjust.CENTER))
                table[-1].append(Sep.DOUBLE)
            table.append(Sep.DOUBLE)

        # Add the padding to the cells.
        for line in table.lines:
            for cell in line.cells:
                cell.value = f" {cell.value} "
                cell.length += 2

        # Compute the length of each column.
        col_length: Dict[int, int] = defaultdict(lambda: 0)
        max_span = max(cell.h_span for line in table.lines for cell in line.cells)
        for span in range(1, max_span + 1):
            for line in table.lines:
                for cell in line.cells:
                    if cell.h_span != span:
                        continue
                    length = sum(
                        col_length[line.column_of(cell) + i] for i in range(span)
                    ) + (span - 1)
                    delta = cell.length - length
                    col_idx = 0
                    while delta > 0:
                        col_length[line.column_of(cell) + (col_idx % span)] += 1
                        delta -= 1
                        col_idx += 1

        # Update the length of each cell.
        for line in table.lines:
            for cell in line.cells:
                cell.length = sum(
                    col_length[line.column_of(cell) + i] for i in range(cell.h_span)
                ) + (cell.h_span - 1)

        # Update the horizontal span of cells for LaTeX.
        if self._latex:
            lines = list(table.lines)
            for i, line in enumerate(lines):
                if i == len(lines) - 1:
                    break
                next_line = lines[i + 1]
                for cell in line.cells:
                    cell_start = line.column_of(cell)
                    cell_end = cell_start + cell.h_span
                    is_sub_item = False
                    for item in next_line:
                        if isinstance(item, Cell):
                            item_start = next_line.column_of(item)
                            item_end = item_start + item.h_span
                            if cell_start <= item_start:
                                is_sub_item = True
                            if item_end >= cell_end:
                                break
                        else:
                            if item is Sep.DOUBLE and is_sub_item:
                                cell.h_span += 1

        # Print the table.
        if self._latex:
            self.latex_print(table, col_length, flat_col_headers, flat_row_headers)
        else:
            self.term_print(table, col_length)

    # ================================== Format ================================== #

    def latex_print(
        self,
        table: CellTable,
        col_length: Dict[int, int],
        col_headers: List[List[Tuple]],
        row_headers: List[List[Tuple]],
    ) -> None:
        """Prints a table of cells in LaTeX."""
        env = "table*" if self._latex_star else "table"
        self.line(f"\\begin{{{env}}}[{self._latex_pos}]")
        self.line("\\centering")
        self.line(f"\\{self._latex_font_size}")
        self.line(f"\\renewcommand{{\\arraystretch}}{{{self._latex_array_stretch}}}")
        self.line(f"\\def\\hs{{\\hspace{{{self._latex_horizontal_space}cm}}}}")
        num_col = max(col_length) + 1 + len([i for i in table[-2] if i is Sep.DOUBLE])
        self.line("\\begin{tabular}{" + "@{\\hs}c" * num_col + "@{}}")
        self.line("\\toprule")

        num_row_headers = len(row_headers[-1][-1])
        for line_idx in range(1, len(table) - 1, 2):
            line, sep = table[line_idx], table[line_idx + 1]
            for item_idx, item in enumerate(line):
                if item_idx not in [0, len(line) - 1]:
                    self.write(item.fmt(self._latex))
            if sep is Sep.DOUBLE:
                if line_idx // 2 == len(col_headers) - 1:
                    self.line("\\\\\\midrule")
                elif line_idx // 2 < len(col_headers) - 1:
                    self.write("\\\\")
                    start = line.index(Sep.DOUBLE, num_row_headers) // 2 + 2
                    crt_col = 0
                    for item_idx, item in enumerate(line):
                        if item_idx == 0:
                            continue
                        if isinstance(item, Cell):
                            crt_col += item.h_span
                            continue
                        if item is Sep.DOUBLE:
                            crt_col += 1
                        if crt_col < start or item is not Sep.DOUBLE:
                            continue
                        if crt_col - 1 >= start:
                            self.write("\\cmidrule{" + f"{start}-{crt_col-1}" + "}")
                        start = crt_col + 1
                    self.line()
                elif line_idx < len(table) - 2:
                    next_line: CellRow = table[line_idx + 2]
                    start = 1
                    for cell in next_line.cells:
                        if cell.value.strip() == "":
                            start += 1
                        else:
                            break
                    self.line(f"\\\\\\cdashline{{{start}-{crt_col-1}}}")
            else:
                self.line("\\\\")
        self.line("\\\\\\bottomrule")

        self.line("\\end{tabular}")
        self.line(f"\\caption{{{self._latex_caption}}}")
        self.line("\\label{tab:metrics}")
        self.line(f"\\end{{{env}}}")

    def term_print(self, table: CellTable, col_length: Dict[int, int]) -> None:
        """Prints a table of cells in the terminal."""
        prev_line = None
        for line_idx in range(1, len(table), 2):
            line, sep = table[line_idx], table[line_idx - 1]
            self.horizontal_separator(prev_line, line, col_length, sep)
            for item in line:
                self.write(item.fmt(self._latex))
            prev_line = line
        self.horizontal_separator(prev_line, None, col_length, table[-1])

    # ================================ Separators ================================ #

    def horizontal_separator(
        self,
        prev_line: Optional[CellRow],
        next_line: Optional[CellRow],
        col_length: Dict[int, int],
        sep: Sep,
    ) -> None:
        """
        Prints a horizontal separator for the table of metrics.

        Args:
            prev_line (Optional[CellRow]): The line above the separator.
            next_line (Optional[CellRow]): The line bellow the separator.
            col_length (Dict[int, int]): The length of each column.
            sep (Sep): The type of separator to print.
        """

        if sep not in {Sep.SIMPLE, Sep.DOUBLE}:
            raise ValueError(f"Unsupported separator type: {sep}")

        if prev_line is None:
            if next_line is None:
                raise ValueError("Cannot print a separator between two empty lines.")
            self.horizontal_separator_top(next_line, sep)

        elif next_line is None:
            if prev_line is None:
                raise ValueError("Cannot print a separator between two empty lines.")
            self.horizontal_separator_bottom(prev_line, sep)

        else:
            if next_line.num_columns != prev_line.num_columns:
                raise ValueError(
                    "The two lines must have the same number of columns."
                    + f" {next_line.num_columns} != {prev_line.num_columns}"
                )
            self.horizontal_separator_middle(prev_line, next_line, col_length, sep)

        self.line()

    def horizontal_separator_top(self, next_line: CellRow, line_sep: Sep) -> None:
        """Prints the top horizontal separator for the table of metrics."""
        for cell_idx in range(1, len(next_line), 2):
            cell, sep = next_line[cell_idx], next_line[cell_idx - 1]
            if cell_idx == 1:
                if sep is Sep.SIMPLE:
                    self.write("┌" if line_sep is Sep.SIMPLE else "╒")
                else:
                    self.write("╓" if line_sep is Sep.SIMPLE else "╔")
            else:
                if sep is Sep.SIMPLE:
                    self.write("┬" if line_sep is Sep.SIMPLE else "╤")
                else:
                    self.write("╥" if line_sep is Sep.SIMPLE else "╦")
            self.write(("─" if line_sep is Sep.SIMPLE else "═") * cell.length)
        if next_line[-1] is Sep.SIMPLE:
            self.write("┐" if line_sep is Sep.SIMPLE else "╕")
        else:
            self.write("╖" if line_sep is Sep.SIMPLE else "╗")

    def horizontal_separator_bottom(self, prev_line: CellRow, line_sep: Sep) -> None:
        """Prints the bottom horizontal separator for the table of metrics."""
        self.line()
        for cell_idx in range(1, len(prev_line), 2):
            cell, sep = prev_line[cell_idx], prev_line[cell_idx - 1]
            if cell_idx == 1:
                if sep is Sep.SIMPLE:
                    self.write("└" if line_sep is Sep.SIMPLE else "╘")
                else:
                    self.write("╙" if line_sep is Sep.SIMPLE else "╚")
            else:
                if sep is Sep.SIMPLE:
                    self.write("┴" if line_sep is Sep.SIMPLE else "╧")
                else:
                    self.write("╨" if line_sep is Sep.SIMPLE else "╩")
            self.write(("─" if line_sep is Sep.SIMPLE else "═") * cell.length)
        if prev_line[-1] is Sep.SIMPLE:
            self.write("┘" if line_sep is Sep.SIMPLE else "╛")
        else:
            self.write("╜" if line_sep is Sep.SIMPLE else "╝")

    def horizontal_separator_middle(
        self,
        prev_line: CellRow,
        next_line: CellRow,
        col_length: Dict[int, int],
        line_sep: Sep,
    ) -> None:
        """Prints a middle horizontal separator for the table of metrics."""
        if prev_line.num_columns != next_line.num_columns:
            raise ValueError("The two lines must have the same number of columns.")
        if prev_line[0] != next_line[0]:
            raise ValueError("The two lines must start with the same separator.")

        self.line()
        if next_line[1].v_span < 0:
            self.write(str(prev_line[0]))
        else:
            if prev_line[0] is Sep.SIMPLE:
                self.write("├" if line_sep is Sep.SIMPLE else "╞")
            else:
                self.write("╟" if line_sep is Sep.SIMPLE else "╠")

        prev_cell, prev_sep, prev_cell_idx = prev_line[1], prev_line[2], 1
        next_cell, next_sep, next_cell_idx = next_line[1], next_line[2], 1
        for c in sorted(col_length.keys()):
            length = col_length[c]
            end_prev_cell = prev_line.column_of(prev_cell) + prev_cell.h_span - 1 == c
            end_next_cell = next_line.column_of(next_cell) + next_cell.h_span - 1 == c
            self.write(
                (
                    " "
                    if next_cell.v_span < 0
                    else "─" if line_sep is Sep.SIMPLE else "═"
                )
                * length
            )
            if c == prev_line.num_columns - 1:
                if prev_sep != next_sep:
                    raise ValueError("The two lines must end with the same separator.")
                if next_cell.v_span < 0:
                    self.write(str(next_sep))
                else:
                    if prev_sep is Sep.SIMPLE:
                        self.write("┤" if line_sep is Sep.SIMPLE else "╡")
                    else:
                        self.write("╢" if line_sep is Sep.SIMPLE else "╣")
            elif end_prev_cell and end_next_cell:
                if prev_sep != next_sep:
                    raise ValueError("The two lines must have with the same separator.")
                if next_cell.v_span < 0:
                    if next_line[next_cell_idx + 2].v_span < 0:
                        if prev_sep is Sep.SIMPLE:
                            self.write("│")
                        else:
                            self.write("║")
                    else:
                        if prev_sep is Sep.SIMPLE:
                            self.write("├" if line_sep is Sep.SIMPLE else "╞")
                        else:
                            self.write("╟" if line_sep is Sep.SIMPLE else "╠")
                else:
                    if prev_sep is Sep.SIMPLE:
                        self.write("┼" if line_sep is Sep.SIMPLE else "╪")
                    else:
                        self.write("╫" if line_sep is Sep.SIMPLE else "╬")
                prev_cell_idx += 2
                prev_cell, prev_sep = prev_line[prev_cell_idx : prev_cell_idx + 2]
                next_cell_idx += 2
                next_cell, next_sep = next_line[next_cell_idx : next_cell_idx + 2]
            elif end_prev_cell:
                if prev_sep is Sep.SIMPLE:
                    self.write("┴" if line_sep is Sep.SIMPLE else "╧")
                else:
                    self.write("╨" if line_sep is Sep.SIMPLE else "╩")
                prev_cell_idx += 2
                prev_cell, prev_sep = prev_line[prev_cell_idx : prev_cell_idx + 2]
            elif end_next_cell:
                if next_sep is Sep.SIMPLE:
                    self.write("┬" if line_sep is Sep.SIMPLE else "╤")
                else:
                    self.write("╥" if line_sep is Sep.SIMPLE else "╦")
                next_cell_idx += 2
                next_cell, next_sep = next_line[next_cell_idx : next_cell_idx + 2]
            else:
                self.write(
                    (
                        " "
                        if next_cell.v_span < 0
                        else "─" if line_sep is Sep.SIMPLE else "═"
                    )
                )


__all__ = ["TableTerminalWritter"]
