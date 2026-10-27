import os
import sqlite3
import subprocess
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "credentials.db")
IMPORT_SCRIPT = os.path.join(ROOT_DIR, "pipeline", "import_catalog.py")

def run_checks():
    print("==========================================")
    print("      PHASE 2 VERIFICATION SUITE         ")
    print("==========================================")

    # Check 1: Confirm DB file exists
    check1 = os.path.exists(DB_PATH)
    print(f"\n[Check 1] Confirm database file '{DB_PATH}' exists: {'PASS' if check1 else 'FAIL'}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check 2: Print table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    check2 = "credentials" in tables
    print(f"\n[Check 2] Table names in DB: {tables} -> {'PASS' if check2 else 'FAIL'}")

    # Check 3: Print credentials table schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='credentials'")
    schema = cursor.fetchone()
    schema_sql = schema[0] if schema else ""
    check3 = bool(schema_sql)
    print(f"\n[Check 3] Credentials table schema: -> {'PASS' if check3 else 'FAIL'}")
    print(schema_sql)

    # Check 4: Count total rows
    cursor.execute("SELECT COUNT(*) FROM credentials")
    total_rows_initial = cursor.fetchone()[0]
    check4 = (total_rows_initial == 1393)
    print(f"\n[Check 4] Count total rows: {total_rows_initial} (Expected: 1393) -> {'PASS' if check4 else 'FAIL'}")

    # Check 5: Count distinct URLs
    cursor.execute("SELECT COUNT(DISTINCT url) FROM credentials")
    distinct_urls = cursor.fetchone()[0]
    check5 = (distinct_urls == 1393)
    print(f"\n[Check 5] Count distinct URLs: {distinct_urls} (Expected: 1393) -> {'PASS' if check5 else 'FAIL'}")

    # Check 6: Count distinct titles
    cursor.execute("SELECT COUNT(DISTINCT title) FROM credentials")
    distinct_titles = cursor.fetchone()[0]
    check6 = (distinct_titles == 1380)
    print(f"\n[Check 6] Count distinct titles: {distinct_titles} (Expected: 1380) -> {'PASS' if check6 else 'FAIL'}")

    # Check 7: Find duplicate titles
    cursor.execute("""
        SELECT title, COUNT(*) as cnt 
        FROM credentials 
        GROUP BY title 
        HAVING cnt > 1
    """)
    duplicate_titles = cursor.fetchall()
    check7 = (len(duplicate_titles) == 13)
    print(f"\n[Check 7] Find duplicate titles: Found {len(duplicate_titles)} duplicate title groups (Expected: 13) -> {'PASS' if check7 else 'FAIL'}")
    for title, cnt in duplicate_titles[:5]:
        print(f"   - '{title}': {cnt} occurrences")

    # Check 8: Search for "BigQuery" and print 5 matching records
    cursor.execute("""
        SELECT id, title, type, level, duration 
        FROM credentials 
        WHERE title LIKE '%BigQuery%' OR description LIKE '%BigQuery%'
        LIMIT 5
    """)
    bq_records = cursor.fetchall()
    check8 = (len(bq_records) == 5)
    print(f"\n[Check 8] Search for 'BigQuery' (5 matching records): -> {'PASS' if check8 else 'FAIL'}")
    for rec in bq_records:
        print(f"   - [{rec[0]}] {rec[1]} | Type: {rec[2]} | Level: {rec[3]} | Duration: {rec[4]}")

    conn.close()

    # Check 9: Run the import script a second time
    print(f"\n[Check 9] Running import script '{IMPORT_SCRIPT}' a second time...")
    res = subprocess.run([sys.executable, IMPORT_SCRIPT], capture_output=True, text=True)
    check9 = (res.returncode == 0)
    print(f"Import script exit code: {res.returncode} -> {'PASS' if check9 else 'FAIL'}")

    # Check 10: Count rows again and confirm row count did NOT increase
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM credentials")
    total_rows_final = cursor.fetchone()[0]
    conn.close()

    check10 = (total_rows_final == total_rows_initial)
    print(f"\n[Check 10] Count rows post-rerun: {total_rows_final} (Initial: {total_rows_initial}, Delta: {total_rows_final - total_rows_initial}) -> {'PASS' if check10 else 'FAIL'}")

    all_checks = [check1, check2, check3, check4, check5, check6, check7, check8, check9, check10]
    passed_count = sum(1 for c in all_checks if c)
    print("\n" + "=" * 50)
    print(f"FINAL SUMMARY: {passed_count}/10 Checks PASSED")
    print("=" * 50)

if __name__ == "__main__":
    run_checks()
