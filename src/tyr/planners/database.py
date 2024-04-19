import datetime
import random
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import replace
from typing import TYPE_CHECKING, Optional

from tyr.core.paths import TyrPaths
from tyr.patterns.singleton import Singleton
from tyr.problems.model.instance import ProblemInstance

if TYPE_CHECKING:
    from tyr.planners.model.config import RunningMode, SolveConfig
    from tyr.planners.model.result import PlannerResult


class Database(Singleton):
    """Utility class to manage the database."""

    def __post_init__(self) -> None:
        self._create_table()

    @contextmanager
    def database(self):
        """Create a connection to the database.

        Yields:
            Connection: The cursor to communicate with the database.
        """
        conn = sqlite3.connect(TyrPaths().db)
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

    def save_planner_result(self, result: "PlannerResult", max_retry: int = 10):
        """Saves the given result into the database.

        Args:
            result (PlannerResult): The result to save.
        """
        if result.from_database is True:
            return

        try:
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
        except sqlite3.OperationalError as e:
            time.sleep(random.randint(10, 1000) / 1000)
            if max_retry > 0:
                self.save_planner_result(result, max_retry - 1)
            else:
                raise e from e

    # pylint: disable = too-many-arguments
    def load_planner_result(
        self,
        planner_name: str,
        problem: ProblemInstance,
        config: "SolveConfig",
        running_mode: "RunningMode",
        keep_unsupported: bool = False,
    ) -> Optional["PlannerResult"]:
        """Loads the planner result matching the given attributes if any.

        Args:
            planner_name (str): The planner name.
            problem (ProblemInstance): The problem instance.
            config (SolveConfig): The configuration used to solve the problem.
            running_mode (RunningMode): The running mode for the planner resolution.
            keep_unsupported (bool): Whether to keep unsupported results.

        Returns:
            Optional[PlannerResult]: The planner result if present, otherwise None.
        """

        # pylint: disable = import-outside-toplevel
        from tyr.planners.model.result import PlannerResult, PlannerResultStatus

        with self.database() as conn:
            resp = (
                conn.cursor()
                .execute(
                    """
                    SELECT * FROM "results"
                    WHERE "planner"=? AND "problem"=? AND "mode"=? AND "memout"=?
                    ORDER BY "creation" DESC
                    LIMIT 1;
                    """,
                    (planner_name, problem.name, running_mode.name, config.memout),
                )
                .fetchone()
            )

        if (
            resp is None
            or resp[4] == "NOT_RUN"
            or (resp[4] == "UNSUPPORTED" and not keep_unsupported)
        ):
            return None

        if resp[4] == "TIMEOUT" and resp[5] is not None and resp[5] < config.timeout:
            return None

        if resp[5] is not None and resp[5] > config.timeout:
            result = PlannerResult.timeout(problem, planner_name, config, running_mode)
            return replace(result, from_database=True)

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
