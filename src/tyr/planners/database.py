import datetime
import multiprocessing
import random
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import replace
from typing import TYPE_CHECKING, Any, Iterator, List, Optional, Tuple

from tyr.core.paths import TyrPaths
from tyr.patterns.singleton import Singleton
from tyr.problems.model.instance import ProblemInstance

if TYPE_CHECKING:
    from tyr.planners.model.config import RunningMode, SolveConfig
    from tyr.planners.model.planner import Planner
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

    @contextmanager
    def warm_up_database(self):
        """Create a connection to the warm-up database.

        Yields:
            Connection: The cursor to communicate with the warm-up database.
        """
        warm_up_db_path = TyrPaths().warm_up_db
        if warm_up_db_path is None:
            # Fallback to main database if no warm-up database specified
            warm_up_db_path = TyrPaths().db
        
        conn = sqlite3.connect(warm_up_db_path)
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
                    "plan"	TEXT,
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
                    "error msg", "jobs", "memout", "timeout", "creation", "plan"
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    result.planner.name,
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
                    str(result.plan) if result.plan is not None else None,
                ),
            )
            conn.commit()

    # pylint: disable = too-many-arguments, too-many-positional-arguments, too-many-locals
    def _handle_db_response(
        self,
        resp: Any,
        planner: "Planner",
        problem: ProblemInstance,
        config: "SolveConfig",
        running_mode: "RunningMode",
        keep_unsupported: bool,
        force_before_timeout: bool,
        not_run_by_default: bool,
    ) -> Optional["PlannerResult"]:
        # pylint: disable = import-outside-toplevel
        from tyr.planners.model.result import PlannerResult, PlannerResultStatus

        def internal_handle(
            resp: Any,
            planner: "Planner",
            problem: ProblemInstance,
            config: "SolveConfig",
            running_mode: "RunningMode",
            keep_unsupported: bool,
            force_before_timeout: bool,
        ):

            if (
                resp is None
                or resp[4] == "NOT_RUN"
                or (resp[4] == "UNSUPPORTED" and not keep_unsupported)
            ):
                return None

            if (
                resp[4] == "TIMEOUT"
                and resp[5] is not None
                and resp[5] < config.timeout
            ):
                return None

            if resp[5] is not None and resp[5] > config.timeout + config.timeout_offset:
                if running_mode.name == "ANYTIME" and not force_before_timeout:
                    result_before_timeout = self.load_planner_result(
                        planner,
                        problem,
                        config,
                        running_mode,
                        keep_unsupported,
                        force_before_timeout=True,
                    )
                    if result_before_timeout is not None:
                        return result_before_timeout
                result = PlannerResult.timeout(problem, planner, config, running_mode)
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
                params = [
                    planner.name,
                    problem.name,
                    running_mode.name,
                    config.memout,
                    config.timeout + config.timeout_offset,
                    resp[11],
                    (
                        datetime.datetime.fromisoformat(resp[11])
                        # + 10 seconds to avoid issues linked to retried savings
                        - datetime.timedelta(seconds=config.timeout + 10)
                    ).isoformat(),
                ]
                with self.database() as conn:
                    resp_solved = conn.cursor().execute(request, params).fetchone()
                if resp_solved is not None:
                    resp = resp_solved

            return PlannerResult(
                planner,
                problem,
                running_mode,
                status=getattr(PlannerResultStatus, resp[4]),
                config=config,
                computation_time=resp[5],
                plan_quality=resp[6],
                error_message=resp[7],
                from_database=True,
                plan=resp[12],
            )

        result = internal_handle(
            resp,
            planner,
            problem,
            config,
            running_mode,
            keep_unsupported,
            force_before_timeout,
        )
        if result is not None:
            assert result.planner == planner  # nosec: B101
            assert result.problem == problem  # nosec: B101
            assert result.running_mode == running_mode  # nosec: B101
            return result
        if not_run_by_default:
            return PlannerResult.not_run(problem, planner, config, running_mode)
        return None

    # pylint: disable = too-many-arguments, too-many-positional-arguments, too-many-locals
    def load_planner_result(
        self,
        planner: "Planner",
        problem: ProblemInstance,
        config: "SolveConfig",
        running_mode: "RunningMode",
        keep_unsupported: bool = False,
        force_before_timeout: bool = False,
        not_run_by_default: bool = False,
    ) -> Optional["PlannerResult"]:
        """Load planner result from main database."""
        return self._load_planner_result_from_db(
            self.database,
            "results",
            planner,
            problem,
            config,
            running_mode,
            keep_unsupported,
            force_before_timeout,
            not_run_by_default,
        )

    # pylint: disable = too-many-arguments, too-many-positional-arguments, too-many-locals
    def load_warm_up_planner_result(
        self,
        planner: "Planner",
        problem: ProblemInstance,
        config: "SolveConfig",
        running_mode: "RunningMode",
        keep_unsupported: bool = False,
        force_before_timeout: bool = False,
        not_run_by_default: bool = False,
    ) -> Optional["PlannerResult"]:
        """Load planner result from warm-up database."""
        return self._load_planner_result_from_db(
            self.warm_up_database,
            "warm_up_plans",
            planner,
            problem,
            config,
            running_mode,
            keep_unsupported,
            force_before_timeout,
            not_run_by_default,
        )

    def _load_planner_result_from_db(
        self,
        db_context,
        table_name: str,
        planner: "Planner",
        problem: ProblemInstance,
        config: "SolveConfig",
        running_mode: "RunningMode",
        keep_unsupported: bool = False,
        force_before_timeout: bool = False,
        not_run_by_default: bool = False,
    ) -> Optional["PlannerResult"]:
        """Loads the planner result matching the given attributes if any.

        Args:
            db_context: The database context manager (database or warm_up_database).
            table_name (str): Name of the table to query.
            planner (Planner): The planner.
            problem (ProblemInstance): The problem instance.
            config (SolveConfig): The configuration used to solve the problem.
            running_mode (RunningMode): The running mode for the planner resolution.
            keep_unsupported (bool): Whether to keep unsupported results.
            force_before_timeout (bool): Whether to force the result to compute before the timeout.
            not_run_by_default (bool): Whether to return a not run result by default.

        Returns:
            Optional[PlannerResult]: The planner result if present, otherwise None.
        """
        if table_name == "warm_up_plans":
            # For warm-up database, we don't have memout column
            request = f"""
                        SELECT NULL as id, planner, problem, mode, status, computation, quality, 
                               NULL as "error msg", 1 as jobs, 0 as memout, 0 as timeout,
                               creation, plan
                        FROM "{table_name}"
                        WHERE "planner"=? AND "problem"=? AND "mode"=?
                        ORDER BY "creation" DESC
                        LIMIT 1;
                        """
            params = [planner.name, problem.name, running_mode.name]
        else:
            # For main database
            request = f"""
                        SELECT * FROM "{table_name}"
                        WHERE "planner"=? AND "problem"=? AND "mode"=? AND "memout"=?
                        ORDER BY "creation" DESC
                        LIMIT 1;
                        """
            params = [planner.name, problem.name, running_mode.name, config.memout]
        
        if force_before_timeout and table_name != "warm_up_plans":
            request = request.replace('"memout"=?', '"memout"=? AND "computation"<=?')
            params.append(config.timeout + config.timeout_offset)

        with db_context() as conn:
            resp = conn.cursor().execute(request, params).fetchone()
        return self._handle_db_response(
            resp,
            planner,
            problem,
            config,
            running_mode,
            keep_unsupported,
            force_before_timeout,
            not_run_by_default,
        )

    def _load_multi_planner_results_atomic(
        self,
        requests: List[Tuple["Planner", ProblemInstance, "RunningMode"]],
        config: "SolveConfig",
        keep_unsupported: bool = False,
        force_before_timeout: bool = False,
        not_run_by_default: bool = False,
    ) -> Iterator[Optional["PlannerResult"]]:
        # The max number of parameters in a SQL query is 1000.
        # One request is composed of 3 parameters.
        # The max number of requests is therefore 333.
        assert len(requests) > 0  # nosec: B101
        assert len(requests) <= 333  # nosec: B101

        result_requests = " OR ".join(
            ["(planner=? AND problem=? AND mode=?)"] * len(requests)
        )
        result_requests_params = []
        for planner, problem, mode in requests:
            result_requests_params.extend([planner.name, problem.name, mode.name])

        request = """
            WITH ranked_results AS (
                SELECT
                    *,
                    ROW_NUMBER() OVER (
                        PARTITION BY planner, problem, mode
                        ORDER BY creation DESC
                    ) AS rank
                FROM results
                WHERE (RESULT_REQUESTS_TO_REPLACE) AND memout=?
            )
            SELECT *
            FROM ranked_results
            WHERE rank=1
            ORDER BY planner, problem, mode DESC;
        """
        request = request.replace("RESULT_REQUESTS_TO_REPLACE", result_requests)
        params = result_requests_params + [str(config.memout)]

        if force_before_timeout:
            request = request.replace("memout=?", "memout=? AND computation<=?")
            params.append(str(config.timeout + config.timeout_offset))

        with self.database() as conn:
            resp_list = conn.cursor().execute(request, params).fetchall()

        for planner, problem, mode in requests:

            def filter_callback(planner=planner, problem=problem, mode=mode):
                return lambda x: (
                    x[1] == planner.name and x[2] == problem.name and x[3] == mode.name
                )

            resp_item = next(filter(filter_callback(), resp_list), None)
            yield self._handle_db_response(
                resp_item,
                planner,
                problem,
                config,
                mode,
                keep_unsupported,
                force_before_timeout,
                not_run_by_default,
            )

    def load_multi_planner_results(
        self,
        requests: List[Tuple["Planner", ProblemInstance, "RunningMode"]],
        config: "SolveConfig",
        keep_unsupported: bool = False,
        force_before_timeout: bool = False,
        not_run_by_default: bool = False,
    ) -> Iterator[Optional["PlannerResult"]]:
        """Loads the planner results matching the given requests if any.

        Args:
            requests (List): The list of tuple (planner, problem, mode) to load.
            config (SolveConfig): The configuration used to solve the problem.
            keep_unsupported (bool): Whether to keep unsupported results.
            force_before_timeout (bool): Whether to force the result to compute before the timeout.
            not_run_by_default (bool): Whether to return a not run result by default.

        Returns:
            Iterator[PlannerResult]: An iterator over the planner results.
        """

        for i in range(0, len(requests), 333):
            yield from self._load_multi_planner_results_atomic(
                requests[i : i + 333],
                config,
                keep_unsupported,
                force_before_timeout,
                not_run_by_default,
            )


__all__ = ["Database"]
