import datetime
import sqlite3
from contextlib import contextmanager
from typing import TYPE_CHECKING, Optional

from tyr.core.constants import DB_FILE
from tyr.patterns.singleton import Singleton
from tyr.problems.model.instance import ProblemInstance

if TYPE_CHECKING:
    from tyr.planners.model.config import RunningMode, SolveConfig
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
                CREATE TABLE IF NOT EXISTS "results" (
                    "id"	INTEGER NOT NULL UNIQUE,
                    "planner"	TEXT NOT NULL,
                    "problem"	TEXT NOT NULL,
                    "mode"	TEXT NOT NULL,
                    "status"	TEXT NOT NULL,
                    "computation"	REAL,
                    "quality"	REAL,
                    "error msg"	TEXT,
                    "jobs"	INTEGER NOT NULL,
                    "memout"	INTEGER NOT NULL,
                    "timeout"	INTEGER NOT NULL,
                    "creation"	TEXT NOT NULL,
                    PRIMARY KEY("id" AUTOINCREMENT)
                );
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
                INSERT INTO "results" (
                    "planner", "problem", "mode", "status", "computation", "quality",
                    "error msg", "jobs", "memout", "timeout", "creation"
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    result.planner_name,
                    result.problem.name,
                    result.running_mode.name,
                    result.status.name,
                    result.computation_time,
                    result.plan_quality,
                    result.error_message,
                    result.config.jobs,
                    result.config.memout,
                    result.config.timeout,
                    datetime.datetime.now().isoformat(),
                ),
            )
            conn.commit()

    def load_planner_result(
        self,
        planner_name: str,
        problem: ProblemInstance,
        config: "SolveConfig",
        running_mode: "RunningMode",
    ) -> Optional["PlannerResult"]:
        """Loads the planner result matching the given attributes if any.

        Args:
            planner_name (str): The planner name.
            problem (ProblemInstance): The problem instance.
            config (SolveConfig): The configuration used to solve the problem.
            running_mode (RunningMode): The running mode for the planner resolution.

        Returns:
            Optional[PlannerResult]: The planner result if present, otherwise None.
        """

        # pylint: disable = import-outside-toplevel
        from tyr.planners.model.result import PlannerResult, PlannerResultStatus

        with self.database() as conn:
            candidates = (
                conn.cursor()
                .execute(
                    """
                    SELECT * FROM "results"
                    WHERE "planner"=? AND "problem"=? AND "mode"=?
                    AND "jobs"=? AND "memout"=? AND "timeout"=?
                    """,
                    (
                        planner_name,
                        problem.name,
                        running_mode.name,
                        config.jobs,
                        config.memout,
                        config.timeout,
                    ),
                )
                .fetchall()
            )

        if not candidates:
            return None
        resp = candidates[0]
        return PlannerResult(
            planner_name,
            problem,
            running_mode,
            status=getattr(PlannerResultStatus, resp[4]),
            config=config,
            computation_time=resp[5],
            plan_quality=resp[6],
            error_message=resp[7],
            from_database=True,
        )


__all__ = ["Database"]
