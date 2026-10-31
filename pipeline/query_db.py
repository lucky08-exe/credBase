import sqlite3
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "credentials.db") if os.path.exists(os.path.join(ROOT_DIR, "credentials.db")) else "credentials.db"

import json

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# List tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("=== TABLES ===")
for t in tables:
    print(t[0])

# For each table, show schema and sample rows
for t in tables:
    tname = t[0]
    print(f"\n=== SCHEMA: {tname} ===")
    cur.execute(f"PRAGMA table_info({tname})")
    cols = cur.fetchall()
    for c in cols:
        print(dict(c))
    
    print(f"\n=== SAMPLE ROWS: {tname} (first 3) ===")
    cur.execute(f"SELECT * FROM {tname} LIMIT 3")
    rows = cur.fetchall()
    for r in rows:
        print(dict(r))

conn.close()
