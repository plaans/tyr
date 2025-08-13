from pathlib import Path
import sqlite3


def merge(db_folder: Path, out_db: str):
    """
    Merge the contents of multiple SQLite database files into a single database.

    Args:
        db_folder (Path): The folder containing the SQLite database files to merge.
        out_db (str): The path to the output database file.
    """
    # Get list of database files to process
    db_files = [
        f
        for f in db_folder.iterdir()
        if f.is_file() and f.suffix in [".db", ".sqlite", ".sqlite3"]
    ]
    total_files = len(db_files)

    if total_files == 0:
        print("No database files found to merge.")
        return
    print(f"Merging {total_files} database files into {out_db}")

    # Connect to output database
    db_merged = sqlite3.connect(out_db)
    db_merged_cursor = db_merged.cursor()

    # Create table schema
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
            "plan"	TEXT,
            PRIMARY KEY("id" AUTOINCREMENT)
        );
        """
    )

    # Optimize SQLite settings for bulk operations
    db_merged_cursor.execute("PRAGMA synchronous = OFF")
    db_merged_cursor.execute("PRAGMA journal_mode = MEMORY")
    db_merged_cursor.execute("PRAGMA temp_store = MEMORY")
    db_merged_cursor.execute("PRAGMA cache_size = -64000")  # 64MB cache

    total_rows = 0

    # Process each database file
    for i, db_file in enumerate(db_files, 1):
        print(f"Processing file {i}/{total_files}: {db_file.name}")

        try:
            # Connect to source database
            db = sqlite3.connect(db_file)
            db_cursor = db.cursor()

            # Get all results from source database
            db_cursor.execute(
                """
                SELECT
                    "planner", "problem", "mode", "status", "computation", "quality",
                    "error msg", "jobs", "memout", "timeout", "creation", "plan"
                FROM results
                """
            )
            results = db_cursor.fetchall()

            # Batch insert all results
            if results:
                db_merged_cursor.executemany(
                    """
                    INSERT INTO "results" (
                        "planner", "problem", "mode", "status", "computation", "quality",
                        "error msg", "jobs", "memout", "timeout", "creation", "plan"
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    results,
                )
                total_rows += len(results)
                print(f"  Added {len(results)} rows (total: {total_rows})")

            db_cursor.close()
            db.close()

        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"Error processing {db_file}: {e}")
            continue

    # Commit all inserts
    db_merged.commit()
    print(f"Inserted {total_rows} total rows")

    # Create temporary index for efficient deduplication
    print("Creating temporary index for deduplication...")
    db_merged_cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS temp_dedup_idx ON results (
            "planner", "problem", "mode", "status", "computation", "quality",
            "error msg", "jobs", "memout", "timeout", "creation", "plan"
        )
        """
    )

    # Remove duplicate entries (only run once at the end)
    print("Removing duplicate entries...")
    db_merged_cursor.execute(
        """
        DELETE FROM "results"
        WHERE rowid NOT IN (
            SELECT MIN(rowid)
            FROM "results"
            GROUP BY
                "planner", "problem", "mode", "status", "computation", "quality",
                "error msg", "jobs", "memout", "timeout", "creation", "plan"
        )
        """
    )

    duplicates_removed = db_merged_cursor.rowcount
    print(f"Removed {duplicates_removed} duplicate entries")

    # Drop the temporary index
    db_merged_cursor.execute("DROP INDEX IF EXISTS temp_dedup_idx")

    # Get final count
    db_merged_cursor.execute("SELECT COUNT(*) FROM results")
    final_count = db_merged_cursor.fetchone()[0]
    print(f"Final database contains {final_count} unique entries")

    # Commit changes before changing PRAGMA settings
    db_merged.commit()

    # Restore normal SQLite settings and optimize
    db_merged_cursor.execute("PRAGMA synchronous = NORMAL")
    db_merged_cursor.execute("PRAGMA journal_mode = DELETE")
    db_merged_cursor.execute("VACUUM")

    db_merged_cursor.close()
    db_merged.close()

    print(f"Database merge completed successfully: {out_db}")


if __name__ == "__main__":
    import sys

    BASE = Path(__file__).parent
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "databases"
    output = sys.argv[2] if len(sys.argv) > 2 else (BASE / "merged.sqlite3").as_posix()
    merge(folder, output)
