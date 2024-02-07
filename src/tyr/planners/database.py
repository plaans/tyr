import datetime
import sqlite3
from contextlib import contextmanager
from typing import TYPE_CHECKING, Optional

from tyr.core.constants import DB_FILE
from tyr.patterns.singleton import Singleton
from tyr.problems.model.instance import ProblemInstance

if TYPE_CHECKING:
    from tyr.planners.model.config import RunningMode
    from tyr.planners.model.result import PlannerResult


class Database(Singleton):
    """Utility class to manage the database."""

    def __init__(self) -> None:
        super().__init__()
        self._create_table()

    @contextmanager
    def database(self):
        """Create a connection to the database.

        Yields:
            Connection: The cursor to communicate with the database.
        """
        conn = sqlite3.connect(DB_FILE)
        try:
            yield conn
        finally:
            conn.close()

    def _create_table(self):
        with self.database() as conn:
            conn.cursor().execute(
                """
            CREATE TABLE IF NOT EXISTS planner_results (
                planner_name TEXT,
                problem_name TEXT,
                running_mode TEXT,
                status TEXT,
                computation_time REAL,
                plan_quality REAL,
                error_message TEXT,
                created_at TEXT,
                PRIMARY KEY (planner_name, problem_name, running_mode)
            )
        """
            )
            conn.commit()

    def save_planner_result(self, result: "PlannerResult"):
        """Saves the given result into the database.

        Args:
            result (PlannerResult): The result to save.
        """
        with self.database() as conn:
            conn.cursor().execute(
                """
                INSERT OR REPLACE INTO planner_results (
                    planner_name, problem_name, running_mode, status,
                    computation_time, plan_quality, error_message, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    result.planner_name,
                    result.problem.name,
                    result.running_mode.name,
                    result.status.name,
                    result.computation_time,
                    result.plan_quality,
                    result.error_message,
                    datetime.datetime.now().isoformat(),
                ),
            )
            conn.commit()

    def load_planner_result(
        self,
        planner_name: str,
        problem: ProblemInstance,
        running_mode: "RunningMode",
    ) -> Optional["PlannerResult"]:
        """Loads the planner result matching the given attributes if any.

        Args:
            planner_name (str): The planner name.
            problem (ProblemInstance): The problem instance.
            running_mode (RunningMode): The running mode for the planner resolution.

        Returns:
            Optional[PlannerResult]: The planner result if present, otherwise None.
        """

        # pylint: disable = import-outside-toplevel
        from tyr.planners.model.result import PlannerResult, PlannerResultStatus

        # pylint: disable = line-too-long
        request = f"SELECT * FROM planner_results WHERE planner_name='{planner_name}' AND problem_name='{problem.name}' AND running_mode='{running_mode.name}' LIMIT 1"  # nosec: B608  # noqa: E501
        conn = sqlite3.connect(DB_FILE)
        resp = conn.cursor().execute(request).fetchone()
        if resp is None:
            return None
        return PlannerResult(
            planner_name,
            problem,
            running_mode,
            status=getattr(PlannerResultStatus, resp[3]),
            computation_time=resp[4],
            plan_quality=resp[5],
            error_message=resp[6],
        )
