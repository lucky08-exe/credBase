import sqlite3
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "credentials.db") if os.path.exists(os.path.join(ROOT_DIR, "credentials.db")) else "credentials.db"

import json

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Keywords relevant to first-year students
keywords = [
    'python', 'web', 'API', 'APIs', 'database', 'SQL', 'javascript', 
    'html', 'machine learning', 'AI', 'artificial intelligence', 
    'cloud', 'git', 'data', 'programming', 'app', 'mobile',
    'security', 'networking', 'linux', 'fundamentals', 'introduction',
    'beginner', 'introductory', 'generative', 'prompt', 'LLM',
    'cybersecurity', 'data science', 'analytics'
]

results = {}

for kw in keywords:
    cur.execute("""
        SELECT c.id, c.title, c.description, c.level, c.type, c.duration, c.url
        FROM credentials c
        JOIN credentials_fts fts ON c.id = fts.id
        WHERE credentials_fts MATCH ?
        ORDER BY c.level ASC
        LIMIT 5
    """, (kw,))
    rows = cur.fetchall()
    if rows:
        results[kw] = [dict(r) for r in rows]

# Print grouped results
for kw, items in results.items():
    print(f"\n{'='*60}")
    print(f"KEYWORD: {kw} ({len(items)} results)")
    print('='*60)
    for item in items:
        print(f"  [{item['level']}] {item['title']} ({item['type']}, {item['duration']})")
        print(f"  URL: {item['url']}")

conn.close()
