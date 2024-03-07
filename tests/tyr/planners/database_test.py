import sqlite3
from unittest.mock import MagicMock, patch

import pytest

from tyr.planners.database import Database
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
    return MagicMock()


class TestDatabase:
    @patch("tyr.planners.database.sqlite3.connect")
    def test_create_table(self, connect_mock, database, conn_mock, cursor_mock):
        connect_mock.return_value = conn_mock
        conn_mock.cursor.return_value = cursor_mock

        database._create_table()

        cursor_mock.execute.assert_called_once_with(
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
                INSERT OR REPLACE INTO planner_results (
                    planner_name, problem_name, running_mode, status,
                    computation_time, plan_quality, error_message, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result_mock.planner_name,
                result_mock.problem.name,
                result_mock.running_mode.name,
                result_mock.status.name,
                result_mock.computation_time,
                result_mock.plan_quality,
                result_mock.error_message,
                now,
            ),
        )
        conn_mock.commit.assert_called_once()

    @patch("tyr.planners.database.sqlite3.connect")
    def test_load_planner_result(
        self, connect_mock, database, conn_mock, cursor_mock, result_mock
    ):
        connect_mock.return_value = conn_mock
        conn_mock.cursor.return_value = cursor_mock
        result_mock.status.name = "SOLVED"
        cursor_mock.execute.return_value.fetchone.return_value = (
            result_mock.planner_name,
            result_mock.problem.name,
            result_mock.running_mode.name,
            result_mock.status.name,
            result_mock.computation_time,
            result_mock.plan_quality,
            result_mock.error_message,
        )
        expected = PlannerResult(
            result_mock.planner_name,
            result_mock.problem,
            result_mock.running_mode,
            PlannerResultStatus.SOLVED,
            result_mock.computation_time,
            result_mock.plan_quality,
            result_mock.error_message,
            from_database=True,
        )

        loaded_result = database.load_planner_result(
            result_mock.planner_name, result_mock.problem, result_mock.running_mode
        )

        cursor_mock.execute.assert_called_once_with(
            f"SELECT * FROM planner_results WHERE planner_name='{result_mock.planner_name}' AND problem_name='{result_mock.problem.name}' AND running_mode='{result_mock.running_mode.name}' LIMIT 1"  # nosec: B608 # noqa: E501
        )
        conn_mock.commit.assert_not_called()
        assert loaded_result == expected
