from pathlib import Path

from tyr.core.paths import TyrPaths


class TestPaths:
    def test_singleton(self):
        assert TyrPaths() is TyrPaths()

    def test_logs_default(self):
        assert TyrPaths().logs == TyrPaths().ROOT_DIR / "logs"

    def test_db_default(self):
        assert TyrPaths().db == TyrPaths().ROOT_DIR / "db.sqlite3"

    def test_logs_setter(self):
        try:
            paths = TyrPaths()
            paths.logs = "new_logs"
            assert paths.logs == Path("new_logs").absolute()
        finally:
            # Reset the default logs path
            paths._logs = TyrPaths().ROOT_DIR / "logs"

    def test_db_setter(self):
        try:
            paths = TyrPaths()
            paths.db = "new_db.sqlite3"
            assert paths.db == Path("new_db.sqlite3").absolute()
        finally:
            # Reset the default logs path
            paths._db = TyrPaths().ROOT_DIR / "db.sqlite3"
