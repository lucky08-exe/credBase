import json
import sqlite3
import os
from urllib.parse import urlparse

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(ROOT_DIR, "credentials.db")
JSON_FILE = os.path.join(ROOT_DIR, "data", "catalog.json")

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
            duration_minutes INTEGER
        )
    """)
    conn.commit()

def import_records(conn: sqlite3.Connection, records: list[dict]) -> int:
    """Imports or upserts catalog records into the SQLite database."""
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(credentials)")
    columns = [col[1] for col in cursor.fetchall()]

    if "paid" in columns:
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
        rows_to_insert = [
            (
                derive_id(item.get("url") or ""),
                item.get("title") or "",
                item.get("description") or "",
                item.get("duration") or "",
                item.get("url") or "",
                item.get("type") or "",
                item.get("level") or "",
                1 if item.get("paid") else 0
            )
            for item in records
        ]
    else:
        upsert_sql = """
            INSERT INTO credentials (id, title, description, duration, url, type, level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                duration = EXCLUDED.duration,
                url = EXCLUDED.url,
                type = EXCLUDED.type,
                level = EXCLUDED.level;
        """
        rows_to_insert = [
            (
                derive_id(item.get("url") or ""),
                item.get("title") or "",
                item.get("description") or "",
                item.get("duration") or "",
                item.get("url") or "",
                item.get("type") or "",
                item.get("level") or ""
            )
            for item in records
        ]

    cursor.executemany(upsert_sql, rows_to_insert)
    conn.commit()
    return len(rows_to_insert)

def run_verification_queries(conn: sqlite3.Connection):
    """Runs verification queries to confirm dataset integrity in SQLite."""
    cursor = conn.cursor()

    print("\n" + "=" * 50)
    print("=== VERIFICATION QUERIES ===")
    print("=" * 50)

    # 1. Total count of records
    cursor.execute("SELECT COUNT(*) FROM credentials")
    total_count = cursor.fetchone()[0]
    print(f"\n1. Total records in 'credentials': {total_count}")

    # 2. Breakdown by type
    cursor.execute("SELECT type, COUNT(*) FROM credentials GROUP BY type ORDER BY COUNT(*) DESC")
    type_counts = cursor.fetchall()
    print("\n2. Breakdown by Type:")
    for type_name, count in type_counts:
        display_type = type_name if type_name else "<EMPTY/NULL>"
        print(f"   - {display_type}: {count}")

    # 3. Breakdown by level
    cursor.execute("SELECT level, COUNT(*) FROM credentials GROUP BY level ORDER BY COUNT(*) DESC")
    level_counts = cursor.fetchall()
    print("\n3. Breakdown by Level:")
    for level_name, count in level_counts:
        display_level = level_name if level_name else "<EMPTY/NULL>"
        print(f"   - {display_level}: {count}")

    # 4. Search query sample: "BigQuery"
    cursor.execute("""
        SELECT id, title, type, level, duration
        FROM credentials
        WHERE title LIKE '%BigQuery%' OR description LIKE '%BigQuery%'
        LIMIT 5
    """)
    search_results = cursor.fetchall()
    print(f"\n4. Sample search for 'BigQuery' (first {len(search_results)} results):")
    for r in search_results:
        print(f"   - [{r[0]}] {r[1]} (Type: {r[2]}, Level: {r[3]}, Duration: {r[4]})")

    # 5. Check duplicate IDs or URLs
    cursor.execute("SELECT id, COUNT(*) FROM credentials GROUP BY id HAVING COUNT(*) > 1")
    dup_ids = cursor.fetchall()
    print(f"\n5. Duplicate IDs count: {len(dup_ids)}")

    cursor.execute("SELECT url, COUNT(*) FROM credentials GROUP BY url HAVING COUNT(*) > 1")
    dup_urls = cursor.fetchall()
    print(f"   Duplicate URLs count: {len(dup_urls)}")

    print("\n" + "=" * 50)
    print("Verification complete.")
    print("=" * 50 + "\n")

def main():
    if not os.path.exists(JSON_FILE):
        raise FileNotFoundError(f"Source JSON file not found at '{JSON_FILE}'.")

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"Loaded {len(records)} records from '{JSON_FILE}'.")

    conn = sqlite3.connect(DB_FILE)
    try:
        init_db(conn)
        processed_count = import_records(conn, records)
        print(f"Successfully processed {processed_count} records into '{DB_FILE}'.")
        run_verification_queries(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
