import sqlite3
import shutil
import os
import re
from urllib.parse import urlparse, urlunparse

DB_PATH = "credentials.db"
BACKUP_PATH = "credentials.db.bak"

def prepare_database():
    """Ensures a clean backup exists and restores from backup if rerun to capture raw state."""
    if os.path.exists(BACKUP_PATH):
        # Restore credentials.db from backup to ensure repeatable raw state
        shutil.copy2(BACKUP_PATH, DB_PATH)
        print(f"[Backup] Restored raw database from '{BACKUP_PATH}'.")
    elif os.path.exists(DB_PATH):
        # Create initial backup
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"[Backup] Created fresh backup copy: '{BACKUP_PATH}'.")
    else:
        raise FileNotFoundError(f"Database file '{DB_PATH}' does not exist.")

def canonicalize_url(url: str) -> str:
    """Strips transient query parameters (catalog_rank, parent) while preserving path."""
    if not url:
        return ""
    parsed = urlparse(url)
    clean_parsed = parsed._replace(query="", fragment="")
    return urlunparse(clean_parsed)

def parse_duration_to_minutes(duration_str: str) -> int | None:
    """Parses duration string into total minutes. Returns None if missing/empty."""
    if not duration_str or not duration_str.strip():
        return None
    
    text = duration_str.lower().strip()
    hours = 0
    minutes = 0
    
    hr_match = re.search(r'(\d+)\s*(?:hour|hr)', text)
    min_match = re.search(r'(\d+)\s*(?:minute|min)', text)
    
    if hr_match:
        hours = int(hr_match.group(1))
    if min_match:
        minutes = int(min_match.group(1))
        
    total = hours * 60 + minutes
    return total if total > 0 else None

def clean_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Fetch raw records to capture BEFORE state for sample reports
    cursor.execute("SELECT id, title, url, level, duration FROM credentials")
    raw_records = cursor.fetchall()

    samples_before = {}
    for id_val, title, url, level, duration in raw_records:
        if id_val == "course_templates_54":
            samples_before["whitespace_title"] = (title, url)
        elif id_val == "course_templates_783":
            samples_before["url_params"] = url
        elif id_val == "course_templates_623":
            samples_before["single_duration"] = (duration, None)
        elif id_val == "course_templates_1206":
            samples_before["multipart_duration"] = (duration, level)

    # 2. Add duration_minutes column if it doesn't exist
    cursor.execute("PRAGMA table_info(credentials)")
    columns = [row[1] for row in cursor.fetchall()]
    if "duration_minutes" not in columns:
        cursor.execute("ALTER TABLE credentials ADD COLUMN duration_minutes INTEGER")
        conn.commit()

    # 3. Perform data cleaning and transformations
    updated_rows = []
    for id_val, title, url, level, duration in raw_records:
        clean_title = title.strip() if title else ""
        clean_url = canonicalize_url(url)
        clean_level = level.strip() if level and level.strip() else None
        duration_mins = parse_duration_to_minutes(duration)

        updated_rows.append((clean_title, clean_url, clean_level, duration_mins, id_val))

    # 4. Update database
    update_sql = """
        UPDATE credentials
        SET title = ?,
            url = ?,
            level = ?,
            duration_minutes = ?
        WHERE id = ?
    """
    cursor.executemany(update_sql, updated_rows)
    conn.commit()
    print(f"[Cleaning] Applied Phase 3B transformations to {len(updated_rows)} records in '{DB_PATH}'.")

    conn.close()
    return samples_before

def verify_cleaning(samples_before):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n" + "=" * 50)
    print("      PHASE 3B — VERIFICATION & CHECKS         ")
    print("=" * 50)

    # 1. Total records count check
    cursor.execute("SELECT COUNT(*) FROM credentials")
    total_count = cursor.fetchone()[0]
    check1 = (total_count == 1393)
    print(f"[Check 1] Total records is still 1,393: {total_count} -> {'PASS' if check1 else 'FAIL'}")

    # 2. No titles have leading/trailing whitespace
    cursor.execute("SELECT COUNT(*) FROM credentials WHERE title != TRIM(title)")
    ws_count = cursor.fetchone()[0]
    check2 = (ws_count == 0)
    print(f"[Check 2] No titles have leading/trailing whitespace: {ws_count} -> {'PASS' if check2 else 'FAIL'}")

    # 3. No URLs contain catalog_rank or parent
    cursor.execute("SELECT COUNT(*) FROM credentials WHERE url LIKE '%catalog_rank%' OR url LIKE '%parent=%'")
    param_url_count = cursor.fetchone()[0]
    check3 = (param_url_count == 0)
    print(f"[Check 3] No URLs contain catalog_rank/parent query parameters: {param_url_count} -> {'PASS' if check3 else 'FAIL'}")

    # 4. All URLs remain valid Google Skills URLs
    cursor.execute("SELECT COUNT(*) FROM credentials WHERE url NOT LIKE 'https://www.skills.google/%'")
    invalid_url_count = cursor.fetchone()[0]
    check4 = (invalid_url_count == 0)
    print(f"[Check 4] All URLs remain valid Google Skills URLs: {invalid_url_count} invalid -> {'PASS' if check4 else 'FAIL'}")

    # 5. Empty levels have become NULL & non-empty levels unchanged
    cursor.execute("SELECT COUNT(*) FROM credentials WHERE level = ''")
    empty_level_str_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM credentials WHERE level IS NULL")
    null_level_count = cursor.fetchone()[0]
    check5 = (empty_level_str_count == 0 and null_level_count == 107)
    print(f"[Check 5] Empty levels converted to NULL (0 empty strings, {null_level_count} NULLs): -> {'PASS' if check5 else 'FAIL'}")

    # 6. Empty durations have duration_minutes = NULL & non-empty parsed correctly
    cursor.execute("SELECT COUNT(*) FROM credentials WHERE (duration IS NULL OR duration = '') AND duration_minutes IS NOT NULL")
    bad_null_duration = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM credentials WHERE duration IS NOT NULL AND duration != '' AND duration_minutes IS NULL")
    bad_parsed_duration = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM credentials WHERE duration_minutes IS NOT NULL")
    parsed_duration_count = cursor.fetchone()[0]
    check6 = (bad_null_duration == 0 and bad_parsed_duration == 0 and parsed_duration_count == 1393)
    print(f"[Check 6] Duration parsing correctness (100% of 1,393 durations parsed into duration_minutes): -> {'PASS' if check6 else 'FAIL'}")

    # 7. Duplicate titles still present & no duplicate URLs introduced
    cursor.execute("SELECT COUNT(DISTINCT title) FROM credentials")
    distinct_titles = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT url) FROM credentials")
    distinct_urls = cursor.fetchone()[0]
    check7 = (distinct_titles == 1380 and distinct_urls == 1393)
    print(f"[Check 7] Duplicate titles preserved ({distinct_titles} unique titles) & unique URLs ({distinct_urls}): -> {'PASS' if check7 else 'FAIL'}")

    # 8. Print Before/After Examples
    print("\n" + "=" * 50)
    print("=== BEFORE / AFTER EXAMPLES ===")
    print("=" * 50)

    # Example 1: Whitespace-padded title
    cursor.execute("SELECT title FROM credentials WHERE id = 'course_templates_54'")
    after_title = cursor.fetchone()[0]
    print("\n1. Whitespace-padded title (ID: course_templates_54):")
    print(f"   BEFORE: '{samples_before['whitespace_title'][0]}'")
    print(f"   AFTER : '{after_title}'")

    # Example 2: URL with query parameters
    cursor.execute("SELECT url FROM credentials WHERE id = 'course_templates_783'")
    after_url = cursor.fetchone()[0]
    print("\n2. URL with query parameters (ID: course_templates_783):")
    print(f"   BEFORE: {samples_before['url_params']}")
    print(f"   AFTER : {after_url}")

    # Example 3: Multi-part duration
    cursor.execute("SELECT duration, duration_minutes FROM credentials WHERE id = 'course_templates_1206'")
    row_mp = cursor.fetchone()
    print("\n3. Multi-part duration (ID: course_templates_1206):")
    print(f"   BEFORE: '{samples_before['multipart_duration'][0]}'")
    print(f"   AFTER : duration_minutes = {row_mp[1]} minutes")

    # Example 4: Missing level record
    cursor.execute("SELECT level, duration, duration_minutes FROM credentials WHERE id = 'course_templates_1206'")
    row_ml = cursor.fetchone()
    print("\n4. Record with missing level (ID: course_templates_1206):")
    print(f"   BEFORE: level='{samples_before['multipart_duration'][1]}' (empty string)")
    print(f"   AFTER : level={row_ml[0]} (NULL)")

    conn.close()

def main():
    prepare_database()
    samples_before = clean_database()
    verify_cleaning(samples_before)

if __name__ == "__main__":
    main()
