import os
import sqlite3
import json
import re
from collections import Counter
from urllib.parse import urlparse

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "credentials.db")

def run_audit():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("==================================================")
    print("      DATA AUDIT REPORT (CREDENTIALS DATASET)     ")
    print("==================================================")

    # 1. Total records
    cursor.execute("SELECT COUNT(*) FROM credentials")
    total_records = cursor.fetchone()[0]
    print(f"\n1. TOTAL RECORDS: {total_records}")

    # 2. Columns in table
    cursor.execute("PRAGMA table_info(credentials)")
    table_columns = [col[1] for col in cursor.fetchall()]

    print("\n2. NULL / EMPTY VALUES PER COLUMN:")
    null_counts = {}
    for col in table_columns:
        cursor.execute(f"SELECT COUNT(*) FROM credentials WHERE {col} IS NULL OR TRIM(CAST({col} AS TEXT)) = ''")
        empty_cnt = cursor.fetchone()[0]
        null_counts[col] = empty_cnt
        print(f" - {col:<16}: {empty_cnt} missing/empty ({empty_cnt/total_records*100:.1f}%)")

    # 3. Distinct values and counts for categorical columns
    print("\n3. DISTINCT VALUES AND COUNTS:")
    for col in ["type", "level"]:
        if col in table_columns:
            cursor.execute(f"SELECT {col}, COUNT(*) FROM credentials GROUP BY {col} ORDER BY COUNT(*) DESC")
            val_counts = cursor.fetchall()
            print(f" Column '{col}':")
            for val, count in val_counts:
                display_val = f"'{val}'" if val != "" else "<EMPTY STRING>"
                print(f"   - {display_val:<25}: {count}")

    # 4. Distinct duration strings and their frequencies
    if "duration" in table_columns:
        print("\n4. DISTINCT DURATION STRINGS & FREQUENCIES (Top 10):")
        cursor.execute("SELECT duration, COUNT(*) FROM credentials GROUP BY duration ORDER BY COUNT(*) DESC LIMIT 10")
        duration_counts = cursor.fetchall()
        for dur, count in duration_counts:
            display_dur = f"'{dur}'" if dur != "" else "<EMPTY STRING>"
            print(f"   - {display_dur:<35}: {count}")

    # 5. Duration minutes summary
    if "duration_minutes" in table_columns:
        cursor.execute("SELECT MIN(duration_minutes), AVG(duration_minutes), MAX(duration_minutes) FROM credentials WHERE duration_minutes IS NOT NULL")
        min_m, avg_m, max_m = cursor.fetchone()
        print(f"\n5. DURATION MINUTES STATS: Min={min_m}m, Avg={round(avg_m or 0)}m, Max={max_m}m")

    # 6. Duplicates
    cursor.execute("SELECT url, COUNT(*) FROM credentials GROUP BY url HAVING COUNT(*) > 1")
    dup_urls = cursor.fetchall()
    print(f"\n6. DUPLICATE URLS: {len(dup_urls)}")

    cursor.execute("SELECT title, COUNT(*) FROM credentials GROUP BY title HAVING COUNT(*) > 1")
    dup_titles = cursor.fetchall()
    print(f"   DUPLICATE TITLES: {len(dup_titles)} distinct titles repeated")

    conn.close()
    print("\n==================================================")
    print("AUDIT COMPLETE")
    print("==================================================")

if __name__ == "__main__":
    run_audit()
