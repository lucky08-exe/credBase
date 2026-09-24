import sqlite3
import json
import re
from collections import Counter
from urllib.parse import urlparse

DB_PATH = "credentials.db"

def run_audit():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("==================================================")
    print("      PHASE 3A — DATA AUDIT REPORT (RAW DATA)    ")
    print("==================================================")

    # 1. Total records
    cursor.execute("SELECT COUNT(*) FROM credentials")
    total_records = cursor.fetchone()[0]
    print(f"\n1. TOTAL RECORDS: {total_records}")

    # 2. NULL / empty values for every column
    columns = ["id", "title", "description", "duration", "url", "type", "level", "paid"]
    print("\n2. NULL / EMPTY VALUES PER COLUMN:")
    null_counts = {}
    for col in columns:
        cursor.execute(f"SELECT COUNT(*) FROM credentials WHERE {col} IS NULL OR TRIM(CAST({col} AS TEXT)) = ''")
        empty_cnt = cursor.fetchone()[0]
        null_counts[col] = empty_cnt
        print(f" - {col:<12}: {empty_cnt} missing/empty ({empty_cnt/total_records*100:.1f}%)")

    # 3. Distinct values and counts for type, level, paid
    print("\n3. DISTINCT VALUES AND COUNTS:")
    for col in ["type", "level", "paid"]:
        cursor.execute(f"SELECT {col}, COUNT(*) FROM credentials GROUP BY {col} ORDER BY COUNT(*) DESC")
        val_counts = cursor.fetchall()
        print(f" Column '{col}':")
        for val, count in val_counts:
            display_val = f"'{val}'" if val != "" else "<EMPTY STRING>"
            print(f"   - {display_val:<25}: {count}")

    # 4. Distinct duration strings and their frequencies
    print("\n4. DISTINCT DURATION STRINGS & FREQUENCIES:")
    cursor.execute("SELECT duration, COUNT(*) FROM credentials GROUP BY duration ORDER BY COUNT(*) DESC")
    duration_counts = cursor.fetchall()
    print(f" Total distinct duration formats: {len(duration_counts)}")
    for dur, count in duration_counts:
        display_dur = f"'{dur}'" if dur != "" else "<EMPTY STRING>"
        print(f"   - {display_dur:<35}: {count}")

    # 5. Duplicate URLs
    print("\n5. DUPLICATE URLS:")
    cursor.execute("SELECT url, COUNT(*) FROM credentials GROUP BY url HAVING COUNT(*) > 1")
    dup_urls = cursor.fetchall()
    print(f" Duplicate URLs found: {len(dup_urls)}")

    # 6. Duplicate titles and their counts
    print("\n6. DUPLICATE TITLES:")
    cursor.execute("SELECT title, COUNT(*) FROM credentials GROUP BY title HAVING COUNT(*) > 1 ORDER BY COUNT(*) DESC")
    dup_titles = cursor.fetchall()
    print(f" Total duplicate title groups: {len(dup_titles)}")
    for title, count in dup_titles:
        print(f"   - '{title}': {count} occurrences")

    # 7. Titles with leading/trailing whitespace
    print("\n7. TITLES WITH LEADING/TRAILING WHITESPACE:")
    cursor.execute("SELECT id, title FROM credentials WHERE title != TRIM(title)")
    whitespace_titles = cursor.fetchall()
    print(f" Titles with leading/trailing whitespace: {len(whitespace_titles)}")
    for id_val, title in whitespace_titles:
        print(f"   - [{id_val}] '{title}'")

    # 8. Descriptions that are empty
    print("\n8. EMPTY DESCRIPTIONS:")
    cursor.execute("SELECT COUNT(*) FROM credentials WHERE description IS NULL OR TRIM(description) = ''")
    empty_desc_cnt = cursor.fetchone()[0]
    print(f" Total empty descriptions: {empty_desc_cnt}")

    # 9. Descriptions that look suspiciously duplicated or malformed
    print("\n9. MALFORMED OR SUSPICIOUS DESCRIPTIONS:")
    # Check duplicate descriptions
    cursor.execute("SELECT description, COUNT(*) FROM credentials WHERE description IS NOT NULL AND description != '' GROUP BY description HAVING COUNT(*) > 1 ORDER BY COUNT(*) DESC")
    dup_descs = cursor.fetchall()
    print(f" Distinct duplicated descriptions: {len(dup_descs)}")
    for desc, count in dup_descs[:5]:
        snippet = desc[:70] + "..." if len(desc) > 70 else desc
        print(f"   - ({count} times) '{snippet}'")

    # Check for HTML tags or unescaped entities in descriptions
    cursor.execute("SELECT id, title, description FROM credentials WHERE description LIKE '%<%>' OR description LIKE '%&lt;%' OR description LIKE '%&gt;%'")
    html_descs = cursor.fetchall()
    print(f" Descriptions with raw HTML tags or unescaped HTML entities: {len(html_descs)}")
    for id_val, title, desc in html_descs[:5]:
        print(f"   - [{id_val}] {title}: '{desc[:80]}...'")

    # 10. URLs that are not valid Google Skills URLs
    print("\n10. INVALID URLS:")
    cursor.execute("SELECT id, url FROM credentials")
    all_urls = cursor.fetchall()
    invalid_urls = []
    for id_val, url in all_urls:
        parsed = urlparse(url)
        if not (parsed.scheme in ["http", "https"] and "skills.google" in parsed.netloc):
            invalid_urls.append((id_val, url))
    print(f" Invalid Google Skills URLs: {len(invalid_urls)}")

    # 11. Other obvious data-quality problems
    print("\n11. OTHER DATA QUALITY ISSUES:")
    # Check for catalog_rank tracking parameters in URLs
    cursor.execute("SELECT COUNT(*) FROM credentials WHERE url LIKE '%catalog_rank=%'")
    tracking_urls = cursor.fetchone()[0]
    print(f" URLs containing transient 'catalog_rank' tracking query parameters: {tracking_urls}")

    # Check for non-standard duration formats
    cursor.execute("SELECT id, title, duration FROM credentials WHERE duration NOT LIKE '%minute%' AND duration NOT LIKE '%hour%' AND duration NOT LIKE '%day%' AND duration != ''")
    odd_durations = cursor.fetchall()
    print(f" Non-standard duration entries: {len(odd_durations)}")
    for id_val, title, dur in odd_durations[:5]:
        print(f"   - [{id_val}] {title}: '{dur}'")

    conn.close()

if __name__ == "__main__":
    run_audit()
