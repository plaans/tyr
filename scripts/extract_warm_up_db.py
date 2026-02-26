#!/usr/bin/env python3
"""
Extract warm-up database from the main database file.

This script creates a lightweight database containing only the data needed
by warm-up planners, significantly reducing disk usage during SLURM runs.
"""
import sqlite3
import sys
from pathlib import Path


def extract_warm_up_database(source_db: str, output_db: str):
    """
    Extract warm-up planning data from the source database.
    
    Args:
        source_db (str): Path to the source database file
        output_db (str): Path to the output warm-up database file
    """
    print(f"Extracting warm-up database from {source_db}")
    
    # Connect to source database
    source_conn = sqlite3.connect(source_db)
    source_cursor = source_conn.cursor()
    
    # Get statistics from source database
    source_cursor.execute("SELECT COUNT(*) FROM results")
    total_rows = source_cursor.fetchone()[0]
    print(f"Source database contains {total_rows} rows")
    
    # Create output database
    output_conn = sqlite3.connect(output_db)
    output_cursor = output_conn.cursor()
    
    # Create warm_up_plans table with minimal schema
    output_cursor.execute("""
        CREATE TABLE IF NOT EXISTS "warm_up_plans" (
            "planner" TEXT NOT NULL,
            "problem" TEXT NOT NULL,
            "mode" TEXT NOT NULL,
            "status" TEXT NOT NULL,
            "computation" REAL,
            "quality" REAL,
            "plan" TEXT,
            "creation" TEXT NOT NULL,
            PRIMARY KEY("planner", "problem", "mode", "creation")
        )
    """)
    
    # Create index for efficient lookups
    output_cursor.execute("""
        CREATE INDEX IF NOT EXISTS "idx_warm_up_lookup" 
        ON "warm_up_plans" ("planner", "problem", "mode", "creation" DESC)
    """)
    
    # Warm-up planners that need database access
    warm_up_planners = ['lpg', 'optic', 'tamer', 'tflap', 'nextflap']
    
    # Extract data for warm-up planners
    placeholders = ','.join(['?'] * len(warm_up_planners))
    query = f"""
        SELECT 
            "planner", "problem", "mode", "status", "computation", "quality", 
            "plan", "creation"
        FROM "results" 
        WHERE "planner" IN ({placeholders})
          AND "status" = 'SOLVED'
          AND "plan" IS NOT NULL
        ORDER BY "planner", "problem", "mode", "creation" DESC
    """
    
    print(f"Extracting data for warm-up planners: {', '.join(warm_up_planners)}")
    source_cursor.execute(query, warm_up_planners)
    
    # Batch insert the results
    warm_up_rows = source_cursor.fetchall()
    if warm_up_rows:
        output_cursor.executemany("""
            INSERT OR REPLACE INTO "warm_up_plans" 
            ("planner", "problem", "mode", "status", "computation", "quality", "plan", "creation")
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, warm_up_rows)
        
        print(f"Extracted {len(warm_up_rows)} rows for warm-up planners")
    else:
        print("Warning: No data found for warm-up planners")
    
    # Commit and get final statistics
    output_conn.commit()
    
    output_cursor.execute("SELECT COUNT(*) FROM warm_up_plans")
    extracted_rows = output_cursor.fetchone()[0]
    
    # Get database sizes
    source_size = Path(source_db).stat().st_size
    output_size = Path(output_db).stat().st_size
    
    reduction_ratio = (1 - output_size / source_size) * 100
    
    print(f"\nExtraction completed:")
    print(f"  Source database: {source_size / (1024**2):.1f} MB ({total_rows} rows)")
    print(f"  Warm-up database: {output_size / (1024**2):.1f} MB ({extracted_rows} rows)")
    print(f"  Size reduction: {reduction_ratio:.1f}%")
    
    # Close connections
    source_cursor.close()
    source_conn.close()
    output_cursor.close()
    output_conn.close()
    
    print(f"Warm-up database created: {output_db}")


def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: python extract_warm_up_db.py <source_db> <output_db>")
        print("Example: python extract_warm_up_db.py final_db.sqlite3 warm_up_plans.sqlite3")
        sys.exit(1)
    
    source_db = sys.argv[1]
    output_db = sys.argv[2]
    
    # Check if source database exists
    if not Path(source_db).exists():
        print(f"Error: Source database '{source_db}' does not exist")
        sys.exit(1)
    
    # Create output directory if needed
    output_path = Path(output_db)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    extract_warm_up_database(source_db, output_db)


if __name__ == "__main__":
    main()