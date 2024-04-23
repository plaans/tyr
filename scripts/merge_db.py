from pathlib import Path
import sqlite3


def merge(db_folder: Path, out_db: str):
    """
    Merge the contents of multiple SQLite database files into a single database.

    Args:
        db_folder (Path): The folder containing the SQLite database files to merge.
        out_db (str): The path to the output database file.
    """
    db_merged = sqlite3.connect(out_db)
    db_merged_cursor = db_merged.cursor()
    db_merged_cursor.execute(
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
    db_merged.commit()

    for db_file in db_folder.iterdir():
        db = sqlite3.connect(db_file)
        db_cursor = db.cursor()
        db_cursor.execute(
            """
            SELECT
                "planner", "problem", "mode", "status", "computation", "quality",
                "error msg", "jobs", "memout", "timeout", "creation"
            FROM results
            """
        )
        results = db_cursor.fetchall()
        for result in results:
            db_merged_cursor.execute(
                """
                INSERT INTO "results" (
                    "planner", "problem", "mode", "status", "computation", "quality",
                    "error msg", "jobs", "memout", "timeout", "creation"
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                result,
            )
        db_merged.commit()
        db_cursor.close()
        db.close()

    db_merged_cursor.close()
    db_merged.close()


if __name__ == "__main__":
    import sys

    BASE = Path(__file__).parent
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "databases"
    output = sys.argv[2] if len(sys.argv) > 2 else (BASE / "merged.sqlite3").as_posix()
    merge(folder, output)
