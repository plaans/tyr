from pathlib import Path
import sqlite3


def merge(db_folder: Path, out_db: str, batch_size: int = 50):
    """
    Merge the contents of multiple SQLite database files into a single database
    with incremental processing and deduplication.

    Args:
        db_folder (Path): The folder containing the SQLite database files to merge.
        out_db (str): The path to the output database file.
        batch_size (int): Number of files to process in each batch.
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
    print(f"Merging {total_files} database files into {out_db} (batch size: {batch_size})")

    # Connect to output database
    db_merged = sqlite3.connect(out_db)
    db_merged_cursor = db_merged.cursor()

    # Create table schema with UNIQUE constraint for deduplication
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
            PRIMARY KEY("id" AUTOINCREMENT),
            UNIQUE("planner", "problem", "mode", "status", "computation", 
                   "quality", "error msg", "jobs", "memout", "timeout", 
                   "creation", "plan")
        );
        """
    )

    # Optimize SQLite settings for bulk operations
    db_merged_cursor.execute("PRAGMA synchronous = OFF")
    db_merged_cursor.execute("PRAGMA journal_mode = MEMORY")
    db_merged_cursor.execute("PRAGMA temp_store = MEMORY")
    db_merged_cursor.execute("PRAGMA cache_size = -64000")  # 64MB cache

    total_rows = 0
    total_duplicates = 0

    # Process database files in batches
    for batch_start in range(0, total_files, batch_size):
        batch_end = min(batch_start + batch_size, total_files)
        batch_files = db_files[batch_start:batch_end]
        
        print(f"\n--- Processing batch {batch_start // batch_size + 1}/{(total_files - 1) // batch_size + 1} "
              f"({len(batch_files)} files) ---")
        
        # Start transaction for this batch
        db_merged_cursor.execute("BEGIN TRANSACTION")
        
        batch_rows = 0
        batch_duplicates = 0

        # Process each database file in the batch
        for i, db_file in enumerate(batch_files, batch_start + 1):
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

                # Insert results with deduplication
                if results:
                    for result in results:
                        try:
                            db_merged_cursor.execute(
                                """
                                INSERT OR IGNORE INTO "results" (
                                    "planner", "problem", "mode", "status", "computation", "quality",
                                    "error msg", "jobs", "memout", "timeout", "creation", "plan"
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """,
                                result,
                            )
                            if db_merged_cursor.rowcount == 0:
                                batch_duplicates += 1
                            else:
                                batch_rows += 1
                        except sqlite3.IntegrityError:
                            # Duplicate entry
                            batch_duplicates += 1
                    
                    print(f"  Added {len(results) - batch_duplicates} rows, skipped {batch_duplicates} duplicates")

                db_cursor.close()
                db.close()

            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Error processing {db_file}: {e}")
                continue
        
        # Commit the batch
        db_merged_cursor.execute("COMMIT")
        total_rows += batch_rows
        total_duplicates += batch_duplicates
        
        print(f"Batch completed: {batch_rows} new rows, {batch_duplicates} duplicates skipped")
        print(f"Running total: {total_rows} rows, {total_duplicates} duplicates skipped")

    # Final commit
    db_merged.commit()
    print(f"\nMerge completed: {total_rows} total rows inserted, {total_duplicates} duplicates skipped")

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
    batch_size = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    
    print(f"Merging databases from: {folder}")
    print(f"Output database: {output}")
    print(f"Batch size: {batch_size}")
    print("-" * 50)
    
    merge(folder, output, batch_size)
