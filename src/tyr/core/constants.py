from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent.parent.resolve()
LOGS_DIR = ROOT_DIR / "logs"
DB_FILE = ROOT_DIR / "db.sqlite3"

__all__ = ["ROOT_DIR", "LOGS_DIR", "DB_FILE"]
