import sqlite3
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "credentials.db") if os.path.exists(os.path.join(ROOT_DIR, "credentials.db")) else "credentials.db"

import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# First-year relevant categories with FTS queries
categories = {
    "🐍 Python & Programming": ["python", "programming"],
    "🌐 Web Development": ["web development", "html", "javascript"],
    "🔌 APIs": ["API", "REST"],
    "🗄️ Databases & SQL": ["SQL", "database"],
    "🤖 AI & Machine Learning": ["machine learning", "artificial intelligence", "generative AI", "large language model"],
    "🔐 Cybersecurity": ["cybersecurity", "security"],
    "📊 Data Analytics": ["data analytics", "data analysis"],
    "☁️ Cloud Fundamentals": ["cloud fundamentals", "cloud computing"],
    "🧠 Prompt Engineering": ["prompt engineering", "prompt"],
}

seen_ids = set()

for category, keywords in categories.items():
    print(f"\n{'='*65}")
    print(f"  {category}")
    print(f"{'='*65}")
    
    found = []
    for kw in keywords:
        cur.execute("""
            SELECT c.id, c.title, c.level, c.type, c.duration, c.url
            FROM credentials c
            JOIN credentials_fts fts ON c.id = fts.id
            WHERE credentials_fts MATCH ?
            AND c.level IN ('introductory', 'beginner', '')
            ORDER BY 
                CASE c.level 
                    WHEN 'introductory' THEN 1 
                    WHEN 'beginner' THEN 2 
                    ELSE 3 
                END,
                c.duration_minutes ASC
            LIMIT 8
        """, (kw,))
        for row in cur.fetchall():
            r = dict(row)
            if r['id'] not in seen_ids:
                seen_ids.add(r['id'])
                found.append(r)
        if len(found) >= 5:
            break
    
    if not found:
        # fallback: any level
        for kw in keywords:
            cur.execute("""
                SELECT c.id, c.title, c.level, c.type, c.duration, c.url
                FROM credentials c
                JOIN credentials_fts fts ON c.id = fts.id
                WHERE credentials_fts MATCH ?
                ORDER BY 
                    CASE c.level 
                        WHEN 'introductory' THEN 1 
                        WHEN 'beginner' THEN 2
                        WHEN 'intermediate' THEN 3 
                        ELSE 4 
                    END,
                    c.duration_minutes ASC
                LIMIT 5
            """, (kw,))
            for row in cur.fetchall():
                r = dict(row)
                if r['id'] not in seen_ids:
                    seen_ids.add(r['id'])
                    found.append(r)
            if len(found) >= 3:
                break

    for item in found[:5]:
        level_tag = f"[{item['level']}]" if item['level'] else "[course]"
        print(f"  {level_tag} {item['title']}")
        print(f"     Type: {item['type']} | Duration: {item['duration']}")
        print(f"     URL: {item['url']}")
        print()

conn.close()
