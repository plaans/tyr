import datetime
import multiprocessing
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

    def save_planner_result(self, result: "PlannerResult"):
        """Saves the given result into the database.

        Args:
            result (PlannerResult): The result to save.
        """
        if result.from_database is True:
            return
        p = multiprocessing.Process(
            target=self._save_planner_result_safe,
            args=(result,),
        )
        p.start()

    def _save_planner_result_safe(self, result: "PlannerResult", max_retries: int = 10):
        try:
            self._save_planner_result(result)
        except sqlite3.OperationalError as e:
            time.sleep(random.randint(10, 1000) / 1000)  # nosec: B311
            if max_retries > 0:
                self._save_planner_result_safe(result, max_retries - 1)
            else:
                raise e from e

    def _save_planner_result(self, result: "PlannerResult"):
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

    # pylint: disable = too-many-arguments
    def load_planner_result(
        self,
        planner_name: str,
        problem: ProblemInstance,
        config: "SolveConfig",
        running_mode: "RunningMode",
        keep_unsupported: bool = False,
        force_before_timeout: bool = False,
    ) -> Optional["PlannerResult"]:
        """Loads the planner result matching the given attributes if any.

        Args:
            planner_name (str): The planner name.
            problem (ProblemInstance): The problem instance.
            config (SolveConfig): The configuration used to solve the problem.
            running_mode (RunningMode): The running mode for the planner resolution.
            keep_unsupported (bool): Whether to keep unsupported results.
            force_before_timeout (bool): Whether to force the result to compute before the timeout.

        Returns:
            Optional[PlannerResult]: The planner result if present, otherwise None.
        """

        # pylint: disable = import-outside-toplevel
        from tyr.planners.model.result import PlannerResult, PlannerResultStatus

        request = """
                    SELECT * FROM "results"
                    WHERE "planner"=? AND "problem"=? AND "mode"=? AND "memout"=?
                    ORDER BY "creation" DESC
                    LIMIT 1;
                    """
        params = [planner_name, problem.name, running_mode.name, config.memout]
        if force_before_timeout:
            request = request.replace('"memout"=?', '"memout"=? AND "computation"<=?')
            params.append(config.timeout)

        with self.database() as conn:
            resp = conn.cursor().execute(request, params).fetchone()

        if (
            resp is None
            or resp[4] == "NOT_RUN"
            or (resp[4] == "UNSUPPORTED" and not keep_unsupported)
        ):
            return None

        if resp[4] == "TIMEOUT" and resp[5] is not None and resp[5] < config.timeout:
            return None

        if resp[5] is not None and resp[5] > config.timeout:
            if running_mode.name == "ANYTIME" and not force_before_timeout:
                result_before_timeout = self.load_planner_result(
                    planner_name,
                    problem,
                    config,
                    running_mode,
                    keep_unsupported,
                    force_before_timeout=True,
                )
                if result_before_timeout is not None:
                    return result_before_timeout
            result = PlannerResult.timeout(problem, planner_name, config, running_mode)
            return replace(result, from_database=True)

        if resp[4] != "SOLVED" and running_mode.name == "ANYTIME":
            request = """
                        SELECT * FROM "results"
                        WHERE "planner"=? AND "problem"=? AND "mode"=? AND "memout"=?
                        AND "computation"<=? AND "creation"<=? AND "creation">=?
                        AND "status"="SOLVED"
                        ORDER BY "creation" DESC
                        LIMIT 1;
                        """
            print(
                resp[11],
                (
                    datetime.datetime.fromisoformat(resp[11])
                    - datetime.timedelta(seconds=config.timeout)
                ).isoformat(),
            )
            params = [
                planner_name,
                problem.name,
                running_mode.name,
                config.memout,
                config.timeout,
                resp[11],
                (
                    datetime.datetime.fromisoformat(resp[11])
                    - datetime.timedelta(seconds=config.timeout)
                ).isoformat(),
            ]
            with self.database() as conn:
                resp_solved = conn.cursor().execute(request, params).fetchone()
            if resp_solved is not None:
                resp = resp_solved

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
