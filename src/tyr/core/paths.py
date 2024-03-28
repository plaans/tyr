from pathlib import Path

from tyr.patterns.singleton import Singleton


class TyrPaths(Singleton):
    """Utility class to manage the paths of the project."""

    ROOT_DIR = Path(__file__).parent.parent.parent.parent.resolve()

    def __init__(self) -> None:
        super().__init__()
        self._logs = self.ROOT_DIR / "logs"
        self._db = self.ROOT_DIR / "db.sqlite3"

    @property
    def logs(self):
        """Return the path to the logs directory."""
        return self._logs

    @logs.setter
    def logs(self, value):
        """Set the path to the logs directory."""
        self._logs = Path(value)

    @property
    def db(self):
        """Return the path to the SQLite database file."""
        return self._db

    @db.setter
    def db(self, value):
        """Set the path to the SQLite database file."""
        self._db = Path(value)


__all__ = ["TyrPaths"]
