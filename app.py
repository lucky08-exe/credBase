import os
import sqlite3
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

DB_PATH = os.path.join(os.path.dirname(__file__), "credentials.db")

app = FastAPI(
    title="ascendr. API",
    description="Search, filter, and discover Google Cloud credentials, labs, and courses with ascendr.",
    version="1.0.0"
)

# Enable CORS for cross-origin deployment (e.g. Vercel frontend + Render backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

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
    return {"status": "ok", "total_records": total}

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
        "avg_duration_minutes": avg_duration
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
            SUM(CASE WHEN duration_minutes > 30 AND duration_minutes <= 60 THEN 1 ELSE 0 END) as between_30m_1h,
            SUM(CASE WHEN duration_minutes > 60 AND duration_minutes <= 180 THEN 1 ELSE 0 END) as between_1_3h,
            SUM(CASE WHEN duration_minutes > 180 THEN 1 ELSE 0 END) as over_3h
        FROM credentials
    """)
    dur_row = cursor.fetchone()
    conn.close()

    return {
        "total": sum(type_counts.values()),
        "types": type_counts,
        "levels": level_counts,
        "duration_brackets": {
            "<30m": dur_row[0] or 0,
            "<1h": dur_row[1] or 0,
            "1-3h": dur_row[2] or 0,
            ">3h": dur_row[3] or 0
        }
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
    page_size: int = 24
):
    conn = get_db()
    cursor = conn.cursor()

    conditions = []
    params = []
    use_fts = False
    fts_query = None

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
        # Preserve older shared URLs while using the database's canonical value.
        types = ["learning_path" if t == "path" else t for t in types]
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
            conditions.append("c.duration_minutes IS NOT NULL AND c.duration_minutes > 30 AND c.duration_minutes <= 60")
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

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    # Count total matching
    count_sql = f"SELECT COUNT(*) FROM credentials c{where_clause}"
    cursor.execute(count_sql, params)
    total = cursor.fetchone()[0]

    # Order Clause
    # Default browse (no query, no explicit sort): recommended items first, then alphabetical.
    # When searching or using an explicit sort, recommended pinning is bypassed.
    has_filters = bool(conditions)
    if sort == "duration_asc":
        order_clause = "ORDER BY CASE WHEN c.duration_minutes IS NULL THEN 1 ELSE 0 END, c.duration_minutes ASC, c.title ASC"
    elif sort == "duration_desc":
        order_clause = "ORDER BY CASE WHEN c.duration_minutes IS NULL THEN 1 ELSE 0 END, c.duration_minutes DESC, c.title ASC"
    elif sort == "title_desc":
        order_clause = "ORDER BY c.title DESC"
    elif sort == "title_asc":
        order_clause = "ORDER BY c.title ASC"
    elif sort == "relevance" and use_fts:
        # FTS5 BM25 returns lower scores for stronger matches.
        order_clause = """ORDER BY (
            SELECT bm25(credentials_fts)
            FROM credentials_fts
            WHERE credentials_fts.id = c.id AND credentials_fts MATCH ?
        ) ASC, c.title ASC"""
    elif not has_filters:
        # Default browse: ranked credentials first (1, 2, 3...), then alphabetical
        order_clause = "ORDER BY CASE WHEN c.rank IS NOT NULL THEN 0 ELSE 1 END, c.rank ASC, c.title ASC"
    else:
        order_clause = "ORDER BY c.title ASC"

    # Pagination
    p = max(1, page if isinstance(page, int) else 1)
    ps = max(1, min(100, page_size if isinstance(page_size, int) else 24))
    offset = (p - 1) * ps

    query_sql = f"""
        SELECT c.id, c.title, c.description, c.duration, c.duration_minutes, c.url, c.type, c.level, c.rank, CASE WHEN c.rank IS NOT NULL THEN 1 ELSE 0 END as recommended
        FROM credentials c
        {where_clause}
        {order_clause}
        LIMIT ? OFFSET ?
    """
    
    query_params = params.copy()
    if sort == "relevance" and use_fts:
        query_params.append(fts_query)
    cursor.execute(query_sql, query_params + [ps, offset])
    rows = cursor.fetchall()

    items = []
    for r in rows:
        item = dict(r)
        item["paid"] = False
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
        SELECT id, title, description, duration, duration_minutes, url, type, level, rank, CASE WHEN rank IS NOT NULL THEN 1 ELSE 0 END as recommended
        FROM credentials
        WHERE id = ?
    """, (credential_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Credential not found")

    item = dict(row)
    item["paid"] = False
    return item

# Mount static folder and Next.js assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
next_dir = os.path.join(static_dir, "_next")

try:
    if os.path.isdir(next_dir):
        app.mount("/_next", StaticFiles(directory=next_dir), name="next_assets")
    if os.path.isdir(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
except Exception as _e:
    print(f"Warning: could not mount static directories — {_e}")

@app.get("/")
def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "ascendr. API is active. Static frontend file not yet created."}

@app.get("/catalogue")
def serve_catalogue():
    cat_file = os.path.join(static_dir, "catalogue.html")
    if os.path.exists(cat_file):
        return FileResponse(cat_file)
    cat_index = os.path.join(static_dir, "catalogue", "index.html")
    if os.path.exists(cat_index):
        return FileResponse(cat_index)
    return serve_index()

@app.get("/paths")
def serve_paths():
    p_file = os.path.join(static_dir, "paths.html")
    if os.path.exists(p_file):
        return FileResponse(p_file)
    p_index = os.path.join(static_dir, "paths", "index.html")
    if os.path.exists(p_index):
        return FileResponse(p_index)
    return serve_index()

@app.get("/paths/{slug}")
def serve_path_detail(slug: str):
    p_file = os.path.join(static_dir, "paths", f"{slug}.html")
    if os.path.exists(p_file):
        return FileResponse(p_file)
    p_index = os.path.join(static_dir, "paths", slug, "index.html")
    if os.path.exists(p_index):
        return FileResponse(p_index)
    return serve_paths()

@app.get("/{filename:path}")
def serve_static_or_spa(filename: str):
    if filename.startswith("api"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    file_path = os.path.join(static_dir, filename)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    html_candidate = os.path.join(static_dir, f"{filename}.html")
    if os.path.isfile(html_candidate):
        return FileResponse(html_candidate)
    index_candidate = os.path.join(static_dir, filename, "index.html")
    if os.path.isfile(index_candidate):
        return FileResponse(index_candidate)
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Not Found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)

# Vercel / AWS Lambda serverless entry point
from mangum import Mangum
handler = Mangum(app)
