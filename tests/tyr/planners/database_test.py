import sqlite3
from unittest.mock import MagicMock, patch

import pytest

from tyr.planners.database import Database
from tyr.planners.model.config import RunningMode
from tyr.planners.model.result import PlannerResult, PlannerResultStatus


@pytest.fixture
def database():
    return Database()


@pytest.fixture
def conn_mock():
    return MagicMock(spec=sqlite3.Connection)


@pytest.fixture
def cursor_mock():
    return MagicMock(spec=sqlite3.Cursor)


@pytest.fixture
def result_mock():
    result = MagicMock()
    result.config.timeout = 10
    result.running_mode = RunningMode.ONESHOT
    yield result


@pytest.fixture
def results_mock():
    return MagicMock()


class TestDatabase:
    @patch("tyr.planners.database.sqlite3.connect")
    def test_create_table(self, connect_mock, database, conn_mock, cursor_mock):
        connect_mock.return_value = conn_mock
        conn_mock.cursor.return_value = cursor_mock

        database._create_table()

        cursor_mock.execute.assert_called_once_with(
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
        conn_mock.commit.assert_called_once()

    @patch("tyr.planners.database.sqlite3.connect")
    @patch("tyr.planners.database.datetime")
    def test_save_planner_result(
        self, datetime_mock, connect_mock, database, conn_mock, cursor_mock, result_mock
    ):
        connect_mock.return_value = conn_mock
        conn_mock.cursor.return_value = cursor_mock
        now = "2021-01-01T00:00:00"
        datetime_mock.datetime.now.return_value.isoformat.return_value = now

        database.save_planner_result(result_mock)

        cursor_mock.execute.assert_called_once_with(
            """
                INSERT INTO "results" (
                    "planner", "problem", "mode", "status", "computation", "quality",
                    "error msg", "jobs", "memout", "timeout", "creation"
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
            (
                result_mock.planner_name,
                result_mock.problem.name,
                result_mock.running_mode.name,
                result_mock.status.name,
                result_mock.computation_time,
                result_mock.plan_quality,
                result_mock.error_message,
                result_mock.config.jobs,
                result_mock.config.memout,
                result_mock.config.timeout,
                now,
            ),
        )
        conn_mock.commit.assert_called_once()

    @patch("tyr.planners.database.sqlite3.connect")
    def test_load_planner_result(
        self,
        connect_mock,
        database,
        conn_mock,
        cursor_mock,
        result_mock,
    ):
        connect_mock.return_value = conn_mock
        conn_mock.cursor.return_value = cursor_mock
        now = "2021-01-01T00:00:00"
        cursor_mock.execute.return_value.fetchone.return_value = (
            1,
            result_mock.planner_name,
            result_mock.problem.name,
            result_mock.running_mode.name,
            "SOLVED",
            5,
            result_mock.plan_quality,
            result_mock.error_message,
            result_mock.config.jobs,
            result_mock.config.memout,
            result_mock.config.timeout,
            now,
        )

        result = database.load_planner_result(
            result_mock.planner_name,
            result_mock.problem,
            result_mock.config,
            result_mock.running_mode,
        )

        assert result == PlannerResult(
            result_mock.planner_name,
            result_mock.problem,
            result_mock.running_mode,
            PlannerResultStatus.SOLVED,
            result_mock.config,
            5,
            result_mock.plan_quality,
            result_mock.error_message,
            True,
        )
        cursor_mock.execute.assert_called_once_with(
            """
                    SELECT * FROM "results"
                    WHERE "planner"=? AND "problem"=? AND "mode"=? AND "memout"=?
                    ORDER BY "creation" DESC
                    LIMIT 1;
                    """,
            (
                result_mock.planner_name,
                result_mock.problem.name,
                result_mock.running_mode.name,
                result_mock.config.memout,
            ),
        )
        conn_mock.commit.assert_not_called()

    @patch("tyr.planners.database.sqlite3.connect")
    def test_load_planner_result_not_found(
        self,
        connect_mock,
        database,
        conn_mock,
        cursor_mock,
        result_mock,
    ):
        connect_mock.return_value = conn_mock
        conn_mock.cursor.return_value = cursor_mock
        cursor_mock.execute.return_value.fetchone.return_value = None

        result = database.load_planner_result(
            result_mock.planner_name,
            result_mock.problem,
            result_mock.config,
            result_mock.running_mode,
        )

        assert result is None

    @patch("tyr.planners.database.sqlite3.connect")
    def test_load_planner_result_after_config_timeout(
        self,
        connect_mock,
        database,
        conn_mock,
        cursor_mock,
        result_mock,
    ):
        connect_mock.return_value = conn_mock
        conn_mock.cursor.return_value = cursor_mock
        now = "2021-01-01T00:00:00"
        cursor_mock.execute.return_value.fetchone.return_value = (
            1,
            result_mock.planner_name,
            result_mock.problem.name,
            result_mock.running_mode.name,
            "SOLVED",
            50,
            result_mock.plan_quality,
            result_mock.error_message,
            result_mock.config.jobs,
            result_mock.config.memout,
            result_mock.config.timeout,
            now,
        )

        result = database.load_planner_result(
            result_mock.planner_name,
            result_mock.problem,
            result_mock.config,
            result_mock.running_mode,
        )

        assert result == PlannerResult(
            str(result_mock.planner_name),
            result_mock.problem,
            result_mock.running_mode,
            PlannerResultStatus.TIMEOUT,
            result_mock.config,
            result_mock.config.timeout,
            None,
            "",
            True,
        )
