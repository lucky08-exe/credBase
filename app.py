import os
import json
import sqlite3
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

DB_PATH = os.path.join(os.path.dirname(__file__), "credentials.db")
ENRICHED_PATH = os.path.join(os.path.dirname(__file__), "enriched_10.json")

# Load enriched data into memory if present
enriched_map = {}
if os.path.exists(ENRICHED_PATH):
    try:
        with open(ENRICHED_PATH, "r", encoding="utf-8") as f:
            for item in json.load(f):
                enriched_map[item["id"]] = item.get("enrichment", {})
    except Exception as e:
        print("Warning loading enriched_10.json:", e)

app = FastAPI(
    title="Google Skills Finder API",
    description="Search, filter, and discover Google Cloud credentials, labs, and courses.",
    version="1.0.0"
)

# Enable CORS for cross-origin deployment (e.g. Vercel frontend + Render backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/api/health")
def health_check():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM credentials")
    total = cursor.fetchone()[0]
    conn.close()
    return {"status": "ok", "total_records": total, "enriched_records": len(enriched_map)}

@app.get("/api/stats")
def get_stats():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM credentials")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT type, COUNT(*) FROM credentials GROUP BY type")
    type_counts = {r[0]: r[1] for r in cursor.fetchall()}

    cursor.execute("SELECT COALESCE(level, 'unspecified'), COUNT(*) FROM credentials GROUP BY level")
    level_counts = {r[0]: r[1] for r in cursor.fetchall()}

    cursor.execute("SELECT AVG(duration_minutes) FROM credentials WHERE duration_minutes IS NOT NULL")
    avg_duration = round(cursor.fetchone()[0] or 0)

    conn.close()
    return {
        "total": total,
        "type_counts": type_counts,
        "level_counts": level_counts,
        "avg_duration_minutes": avg_duration,
        "enriched_count": len(enriched_map)
    }

@app.get("/api/filters")
def get_filters():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT type, COUNT(*) FROM credentials GROUP BY type")
    type_counts = {r[0]: r[1] for r in cursor.fetchall()}

    cursor.execute("""
        SELECT 
            CASE 
                WHEN level IS NULL OR level = '' THEN 'unspecified' 
                ELSE LOWER(level) 
            END as lvl, 
            COUNT(*) 
        FROM credentials 
        GROUP BY lvl
    """)
    level_counts = {r[0]: r[1] for r in cursor.fetchall()}

    cursor.execute("""
        SELECT
            SUM(CASE WHEN duration_minutes <= 30 THEN 1 ELSE 0 END) as under_30m,
            SUM(CASE WHEN duration_minutes <= 60 THEN 1 ELSE 0 END) as under_1h,
            SUM(CASE WHEN duration_minutes > 60 AND duration_minutes <= 180 THEN 1 ELSE 0 END) as between_1_3h,
            SUM(CASE WHEN duration_minutes > 180 THEN 1 ELSE 0 END) as over_3h
        FROM credentials
    """)
    dur_row = cursor.fetchone()
    conn.close()

    return {
        "types": type_counts,
        "levels": level_counts,
        "duration_brackets": {
            "<30m": dur_row[0] or 0,
            "<1h": dur_row[1] or 0,
            "1-3h": dur_row[2] or 0,
            ">3h": dur_row[3] or 0
        },
        "enriched_count": len(enriched_map)
    }

@app.get("/api/credentials")
def list_credentials(
    q: Optional[str] = None,
    type: Optional[str] = None,
    level: Optional[str] = None,
    duration_bracket: Optional[str] = None,
    duration_min: Optional[int] = None,
    duration_max: Optional[int] = None,
    sort: Optional[str] = "relevance",
    page: int = 1,
    page_size: int = 24,
    enriched_only: bool = False
):
    conn = get_db()
    cursor = conn.cursor()

    conditions = []
    params = []
    use_fts = False

    # 1. Search Query
    if q and isinstance(q, str) and q.strip():
        raw_q = q.strip()
        cleaned_words = [w for w in "".join([c if c.isalnum() else " " for c in raw_q]).split() if w]
        if cleaned_words:
            fts_query = " ".join([f'"{w}"*' for w in cleaned_words])
            conditions.append("c.id IN (SELECT id FROM credentials_fts WHERE credentials_fts MATCH ?)")
            params.append(fts_query)
            use_fts = True
        else:
            conditions.append("(c.title LIKE ? OR c.description LIKE ?)")
            params.extend([f"%{raw_q}%", f"%{raw_q}%"])

    # 2. Type filter
    if type and isinstance(type, str) and type.lower() != "all":
        types = [t.strip().lower() for t in type.split(",") if t.strip()]
        if types:
            placeholders = ",".join("?" for _ in types)
            conditions.append(f"LOWER(c.type) IN ({placeholders})")
            params.extend(types)

    # 3. Level filter
    if level and isinstance(level, str) and level.lower() != "all":
        levels = [l.strip().lower() for l in level.split(",") if l.strip()]
        level_conds = []
        for l in levels:
            if l == "unspecified":
                level_conds.append("c.level IS NULL OR c.level = ''")
            else:
                level_conds.append("LOWER(c.level) = ?")
                params.append(l)
        if level_conds:
            conditions.append(f"({' OR '.join(level_conds)})")

    # 4. Duration bracket
    if duration_bracket and isinstance(duration_bracket, str):
        if duration_bracket == "<30m":
            conditions.append("c.duration_minutes IS NOT NULL AND c.duration_minutes <= 30")
        elif duration_bracket == "<1h":
            conditions.append("c.duration_minutes IS NOT NULL AND c.duration_minutes <= 60")
        elif duration_bracket == "1-3h":
            conditions.append("c.duration_minutes IS NOT NULL AND c.duration_minutes > 60 AND c.duration_minutes <= 180")
        elif duration_bracket == ">3h":
            conditions.append("c.duration_minutes IS NOT NULL AND c.duration_minutes > 180")

    if duration_min is not None and isinstance(duration_min, int):
        conditions.append("c.duration_minutes >= ?")
        params.append(duration_min)

    if duration_max is not None and isinstance(duration_max, int):
        conditions.append("c.duration_minutes <= ?")
        params.append(duration_max)

    # 5. Enriched Only
    if enriched_only:
        enriched_ids = list(enriched_map.keys())
        if enriched_ids:
            placeholders = ",".join("?" for _ in enriched_ids)
            conditions.append(f"c.id IN ({placeholders})")
            params.extend(enriched_ids)
        else:
            conditions.append("1=0")

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    # Count total matching
    count_sql = f"SELECT COUNT(*) FROM credentials c{where_clause}"
    cursor.execute(count_sql, params)
    total = cursor.fetchone()[0]

    # Order Clause
    order_clause = "ORDER BY c.title ASC"
    if sort == "duration_asc":
        order_clause = "ORDER BY CASE WHEN c.duration_minutes IS NULL THEN 1 ELSE 0 END, c.duration_minutes ASC, c.title ASC"
    elif sort == "duration_desc":
        order_clause = "ORDER BY CASE WHEN c.duration_minutes IS NULL THEN 1 ELSE 0 END, c.duration_minutes DESC, c.title ASC"
    elif sort == "title_desc":
        order_clause = "ORDER BY c.title DESC"
    elif sort == "title_asc":
        order_clause = "ORDER BY c.title ASC"
    elif sort == "relevance" and use_fts:
        order_clause = "ORDER BY c.id"

    # Pagination
    p = max(1, page if isinstance(page, int) else 1)
    ps = max(1, min(100, page_size if isinstance(page_size, int) else 24))
    offset = (p - 1) * ps

    query_sql = f"""
        SELECT c.id, c.title, c.description, c.duration, c.duration_minutes, c.url, c.type, c.level
        FROM credentials c
        {where_clause}
        {order_clause}
        LIMIT ? OFFSET ?
    """
    
    cursor.execute(query_sql, params + [ps, offset])
    rows = cursor.fetchall()

    items = []
    for r in rows:
        item = dict(r)
        item["paid"] = False
        item["enrichment"] = enriched_map.get(item["id"], None)
        items.append(item)

    conn.close()

    total_pages = (total + ps - 1) // ps if total > 0 else 1
    return {
        "items": items,
        "total": total,
        "page": p,
        "page_size": ps,
        "total_pages": total_pages
    }

@app.get("/api/credentials/{credential_id}")
def get_credential(credential_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, description, duration, duration_minutes, url, type, level
        FROM credentials
        WHERE id = ?
    """, (credential_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Credential not found")

    item = dict(row)
    item["paid"] = False
    item["enrichment"] = enriched_map.get(item["id"], None)
    return item

# Mount static folder (guarded — may not exist in serverless environments)
static_dir = os.path.join(os.path.dirname(__file__), "static")
try:
    if os.path.isdir(static_dir):
        from fastapi.staticfiles import StaticFiles
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
except Exception as _e:
    print(f"Warning: could not mount /static — {_e}")

@app.get("/")
def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Google Skills Finder API is active. Static frontend file not yet created."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

# Vercel / AWS Lambda serverless entry point
from mangum import Mangum
handler = Mangum(app)
