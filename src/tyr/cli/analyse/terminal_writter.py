from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import DefaultDict, Dict, Generator, List, Optional, TextIO, Union

from tyr.cli.collector import CollectionResult
from tyr.cli.writter import Writter
from tyr.configuration.loader import load_config
from tyr.metrics.metric import Metric
from tyr.planners.model.config import SolveConfig
from tyr.planners.model.planner import Planner
from tyr.planners.model.result import PlannerResult
from tyr.problems.model.instance import ProblemInstance


class Adjust(Enum):
    """Enumeration of the possible adjustments for a cell value."""

    CENTER = auto()
    LEFT = auto()
    RIGHT = auto()


class Sep(Enum):
    """Enumeration of the possible separators for a table."""

    SIMPLE = auto()
    DOUBLE = auto()

    def __str__(self) -> str:
        if self is Sep.SIMPLE:
            return "│"
        if self is Sep.DOUBLE:
            return "║"
        raise NotImplementedError(f"{self} is not supported to print a separator")


@dataclass
class Cell:
    """Data class representing a cell in a table."""

    value: str
    adjust: Adjust
    span: int = 1
    length: int = -1

    def __post_init__(self):
        if self.length == -1:
            self.length = len(self.value)

    def __str__(self) -> str:
        if self.adjust == Adjust.CENTER:
            return self.value.center(self.length)
        if self.adjust == Adjust.LEFT:
            return self.value.ljust(self.length)
        if self.adjust == Adjust.RIGHT:
            return self.value.rjust(self.length)
        raise NotImplementedError(f"{self.adjust} is not supported to print a cell")


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
            col += item.span
        raise ValueError(f"{cell} is not in the row.")

    @property
    def num_columns(self) -> int:
        """Returns the number of columns in the row."""
        return sum(cell.span for cell in self.cells)

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


class AnalyzeTerminalWritter(Writter):
    """Terminal writter for the analysis command."""

    def __init__(
        self,
        solve_config: SolveConfig,
        out: Union[Optional[TextIO], List[TextIO]] = None,
        verbosity: int = 0,
        config: Optional[Path] = None,
    ) -> None:
        super().__init__(solve_config, out, verbosity, config)
        self._results: List[PlannerResult] = []
        self._planners: List[Planner] = []
        self._problems: List[ProblemInstance] = []
        self._metrics: List[Metric] = []

    # =============================== Manipulation =============================== #

    def set_results(self, results: List[PlannerResult]):
        """Modifies the stored results.

        Args:
            results (List[Optional[PlannerResult]]): The results to store.
        """
        self._results = results

        total = len(results)
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
        return "analysis"

    # ================================== Analyse ================================= #

    # pylint: disable = too-many-branches, too-many-locals, too-many-statements
    def analyse(self) -> None:
        """Prints a table of metrics based on results."""

        # Get the table configuration from the configuration file.
        # pylint: disable = eval-used
        conf = load_config("", self._config).get("analyse", {}).get("table", {})
        identical = "lambda x: x"
        null = "lambda x: None"
        str_order = "lambda x: (x == '', str(x))"
        mapping_conf = {
            "domain": eval(conf.get("domain_mapping", identical)),  # nosec: B307
            "planner": eval(conf.get("planner_mapping", identical)),  # nosec: B307
            "metric": eval(conf.get("metric_mapping", identical)),  # nosec: B307
            "category": eval(conf.get("category_mapping", null)),  # nosec: B307
        }
        mapping_item = {
            "domain": lambda x: x.name.title().replace("-", " "),
            "planner": lambda x: x.name.title().replace("-", " "),
            "metric": lambda x: x.abbrev()[0].upper() + x.abbrev()[1:],
            "category": lambda x: x,
        }
        mapping = {
            k: lambda x, k=k, v=v: ("" if x is None else v(mapping_item[k](x)).strip())
            for k, v in mapping_conf.items()
        }
        ordering_confg = {
            "domain": eval(conf.get("domain_ordering", str_order)),  # nosec: B307
            "planner": eval(conf.get("planner_ordering", str_order)),  # nosec: B307
            "metric": eval(conf.get("metric_ordering", str_order)),  # nosec: B307
            "category": eval(conf.get("category_ordering", str_order)),  # nosec: B307
        }
        ordering = {
            k: lambda x, k=k, v=v: v(mapping[k](x)) for k, v in ordering_confg.items()
        }

        # Get all domains.
        domains = {p.domain for p in self._problems}

        # Get all categories.
        categories: DefaultDict[str, List[Optional[Planner]]] = defaultdict(list)
        for pl in self._planners:
            categories[mapping["category"](mapping_item["planner"](pl))].append(pl)
        categories[""].append(None)

        # Create the table.
        table = CellTable([Sep.DOUBLE])

        # Create the categories headers.
        if None not in categories:
            table.append(CellRow([Sep.DOUBLE, Cell("", Adjust.CENTER), Sep.DOUBLE]))
            for category in sorted(categories, key=ordering["category"]):
                category_planners = len(categories[category])
                span = category_planners * len(self._metrics)
                table[-1].append(Cell(category, Adjust.CENTER, span))
                table[-1].append(Sep.DOUBLE)
            table.append(Sep.DOUBLE)

        # Create the planners headers.
        table.append(CellRow([Sep.DOUBLE, Cell("Domains", Adjust.CENTER), Sep.DOUBLE]))
        for category in sorted(categories, key=ordering["category"]):
            for p in sorted(categories[category], key=ordering["planner"]):
                planner_name = mapping["planner"](p) if p is not None else "Best"
                table[-1].append(Cell(planner_name, Adjust.CENTER, len(self._metrics)))
                table[-1].append(Sep.DOUBLE)
        table.append(Sep.DOUBLE)

        # Create the metrics headers.
        table.append(CellRow([Sep.DOUBLE, Cell("", Adjust.LEFT), Sep.DOUBLE]))
        for category in sorted(categories, key=ordering["category"]):
            for _ in sorted(categories[category], key=ordering["planner"]):
                for metric in sorted(self._metrics, key=ordering["metric"]):
                    metric_name = mapping["metric"](metric)
                    table[-1].append(Cell(metric_name, Adjust.CENTER))
                    table[-1].append(Sep.SIMPLE)
                table[-1].pop()
                table[-1].append(Sep.DOUBLE)
        table.append(Sep.DOUBLE)

        # Create the cells.
        for domain in sorted(domains, key=ordering["domain"]):
            num_inst = len({id(r) for r in self._results if r.problem.domain == domain})
            num_inst = int(num_inst / len(self._planners))
            domain_name = mapping["domain"](domain) + f" ({num_inst})"
            table.append(
                CellRow([Sep.DOUBLE, Cell(domain_name, Adjust.LEFT), Sep.DOUBLE])
            )
            for category in sorted(categories, key=ordering["category"]):
                for p in sorted(categories[category], key=ordering["planner"]):
                    for metric in sorted(self._metrics, key=ordering["metric"]):
                        if p is not None:
                            results = [
                                result
                                for result in self._results
                                if result.problem.domain == domain
                                and result.planner_name == p.name
                            ]
                            value = metric.evaluate(results)
                        else:
                            results = [
                                result
                                for result in self._results
                                if result.problem.domain == domain
                            ]
                            value = metric.best_across_planners(results)
                        table[-1].append(Cell(value, Adjust.CENTER))
                        table[-1].append(Sep.SIMPLE)
                    table[-1].pop()
                    table[-1].append(Sep.DOUBLE)
            table.append(Sep.SIMPLE)
        table.pop()
        table.append(Sep.DOUBLE)

        # Create the best footer.
        table.append(CellRow([Sep.DOUBLE, Cell("Best", Adjust.CENTER), Sep.DOUBLE]))
        for category in sorted(categories, key=ordering["category"]):
            for p in sorted(categories[category], key=ordering["planner"]):
                if p is None:
                    table[-1].append(Cell("", Adjust.CENTER, len(self._metrics)))
                    table[-1].append(Sep.DOUBLE)
                    continue
                for metric in sorted(self._metrics, key=ordering["metric"]):
                    results = [
                        result
                        for result in self._results
                        if result.planner_name == p.name
                    ]
                    value = metric.best_across_domains(results)
                    table[-1].append(Cell(value, Adjust.CENTER))
                    table[-1].append(Sep.SIMPLE)
                table[-1].pop()
                table[-1].append(Sep.DOUBLE)
        table.append(Sep.DOUBLE)

        # Add the padding to the cells.
        for line in table.lines:
            for cell in line.cells:
                cell.value = f" {cell.value} "
                cell.length += 2

        # Compute the length of each column.
        col_length: Dict[int, int] = defaultdict(lambda: 0)
        max_span = max(cell.span for line in table.lines for cell in line.cells)
        for span in range(1, max_span + 1):
            for line in table.lines:
                for cell in line.cells:
                    if cell.span != span:
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
                    col_length[line.column_of(cell) + i] for i in range(cell.span)
                ) + (cell.span - 1)

        # Print the cells.
        prev_line = None
        for line_idx in range(1, len(table), 2):
            line, sep = table[line_idx], table[line_idx - 1]
            self.horizontal_separator(prev_line, line, col_length, sep)
            for item in line:
                self.write(str(item))
            prev_line = line
        self.horizontal_separator(prev_line, None, col_length, table[-1])

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
                raise ValueError("The two lines must have the same number of columns.")
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
        if prev_line[0] is Sep.SIMPLE:
            self.write("├" if line_sep is Sep.SIMPLE else "╞")
        else:
            self.write("╟" if line_sep is Sep.SIMPLE else "╠")

        prev_cell, prev_sep, prev_cell_idx = prev_line[1], prev_line[2], 1
        next_cell, next_sep, next_cell_idx = next_line[1], next_line[2], 1
        for c, length in col_length.items():
            end_prev_cell = prev_line.column_of(prev_cell) + prev_cell.span - 1 == c
            end_next_cell = next_line.column_of(next_cell) + next_cell.span - 1 == c
            self.write(("─" if line_sep is Sep.SIMPLE else "═") * length)
            if c == prev_line.num_columns - 1:
                if prev_sep != next_sep:
                    raise ValueError("The two lines must end with the same separator.")
                if prev_sep is Sep.SIMPLE:
                    self.write("┤" if line_sep is Sep.SIMPLE else "╡")
                else:
                    self.write("╢" if line_sep is Sep.SIMPLE else "╣")
            elif end_prev_cell and end_next_cell:
                if prev_sep != next_sep:
                    raise ValueError("The two lines must have with the same separator.")
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
                self.write(("─" if line_sep is Sep.SIMPLE else "═"))


__all__ = ["AnalyzeTerminalWritter"]
