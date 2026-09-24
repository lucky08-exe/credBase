import json
import sqlite3
import os
from urllib.parse import urlparse

DB_FILE = "credentials.db"
JSON_FILE = "catalog.json"

def derive_id(url: str) -> str:
    """Derives a stable external identifier from the catalog URL path.
    Example: 'https://www.skills.google/course_templates/783?...' -> 'course_templates_783'
    """
    if not url:
        return ""
    parsed = urlparse(url)
    clean_path = parsed.path.strip("/")
    return clean_path.replace("/", "_")

def init_db(conn: sqlite3.Connection):
    """Creates the credentials table if it does not already exist."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS credentials (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            duration TEXT,
            url TEXT UNIQUE NOT NULL,
            type TEXT,
            level TEXT,
            paid INTEGER NOT NULL
        )
    """)
    conn.commit()

def import_records(conn: sqlite3.Connection, records: list[dict]) -> int:
    """Imports or upserts catalog records into the SQLite database."""
    cursor = conn.cursor()
    upsert_sql = """
        INSERT INTO credentials (id, title, description, duration, url, type, level, paid)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            title = EXCLUDED.title,
            description = EXCLUDED.description,
            duration = EXCLUDED.duration,
            url = EXCLUDED.url,
            type = EXCLUDED.type,
            level = EXCLUDED.level,
            paid = EXCLUDED.paid;
    """
    
    rows_to_insert = []
    for item in records:
        url = item.get("url") or ""
        item_id = derive_id(url)
        title = item.get("title") or ""
        description = item.get("description") or ""
        duration = item.get("duration") or ""
        item_type = item.get("type") or ""
        level = item.get("level") or ""
        paid = 1 if item.get("paid") else 0
        
        rows_to_insert.append((item_id, title, description, duration, url, item_type, level, paid))

    cursor.executemany(upsert_sql, rows_to_insert)
    conn.commit()
    return len(rows_to_insert)

def run_verification_queries(conn: sqlite3.Connection):
    """Runs verification queries to confirm dataset integrity in SQLite."""
    cursor = conn.cursor()

    print("\n" + "=" * 50)
    print("=== VERIFICATION QUERIES ===")
    print("=" * 50)

    # 1. Total records
    cursor.execute("SELECT COUNT(*) FROM credentials")
    total_count = cursor.fetchone()[0]
    print(f"Total records in DB: {total_count}")

    # 2. Number of unique titles
    cursor.execute("SELECT COUNT(DISTINCT title) FROM credentials")
    unique_titles_count = cursor.fetchone()[0]
    print(f"Unique titles count: {unique_titles_count}")

    # 3. Duplicate title groups count
    cursor.execute("""
        SELECT title, COUNT(*) as cnt 
        FROM credentials 
        GROUP BY title 
        HAVING cnt > 1
    """)
    duplicate_groups = cursor.fetchall()
    print(f"Duplicate title groups count: {len(duplicate_groups)}")
    if duplicate_groups:
        print("Sample duplicate titles preserved:")
        for title, count in duplicate_groups[:3]:
            print(f" - '{title}' ({count} records with distinct URLs)")

    # 4. Records matching "BigQuery"
    cursor.execute("""
        SELECT id, title, type, level, duration, paid 
        FROM credentials 
        WHERE title LIKE '%BigQuery%' OR description LIKE '%BigQuery%'
        LIMIT 5
    """)
    bq_records = cursor.fetchall()
    print(f"\nSample records matching 'BigQuery' ({len(bq_records)} shown):")
    for row in bq_records:
        print(f" - [{row[0]}] {row[1]} | Type: {row[2]} | Level: {row[3]} | Paid: {bool(row[5])}")

    # 5. Print a few sample rows
    print("\nSample database rows (First 3):")
    cursor.execute("SELECT id, title, type, duration, url FROM credentials LIMIT 3")
    for row in cursor.fetchall():
        print(f" ID: {row[0]}")
        print(f" Title: {row[1]}")
        print(f" Type: {row[2]} | Duration: {row[3]}")
        print(f" URL: {row[4]}")
        print("-" * 40)

def main():
    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found. Please run Phase 1 first.")
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"Loaded {len(records)} records from '{JSON_FILE}'.")

    conn = sqlite3.connect(DB_FILE)
    try:
        init_db(conn)
        processed_count = import_records(conn, records)
        print(f"Processed {processed_count} records for database import/upsert.")
        
        run_verification_queries(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
