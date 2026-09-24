# Google Skills Finder 🚀

A modern, fast web application and API to search, filter, and discover **1,390+ official Google Cloud credentials**, hands-on labs, skill badge courses, and learning paths.

🔗 **Live Demo**: [credbase.onrender.com](https://credbase.onrender.com)

---

## 🌟 Key Features (V1)

- **⚡ Lightning-Fast Full-Text Search** — SQLite FTS5 with prefix and multi-keyword matching over titles and descriptions.
- **🎯 Multi-Faceted Filters**:
  - **Credential Type**: Hands-on Lab (688), Skill Course (612), Learning Path (93)
  - **Difficulty Level**: Introductory (792), Intermediate (423), Advanced (71), Unspecified (107)
  - **Duration**: Quick (≤ 30 min), Short (≤ 1 hr), Medium (1–3 hrs), Deep Dive (> 3 hrs)
  - **AI Enriched**: Filter for credentials with curated skills and career paths
- **🔄 Instant Sorting** — Relevance, Title (A–Z / Z–A), Shortest / Longest Duration
- **📱 Responsive UI** — Google-inspired design with Tailwind CSS, works on desktop and mobile
- **🔍 Quick View Modal** — Preview title, description, duration, and skills without leaving the page
- **🔗 Direct Canonical Links** — One-click launch into official Google Skills pages
- **🌐 Shareable URLs** — State synced to query params (`?q=Kubernetes&level=intermediate`)

---

## 🛠️ Tech Stack

| Layer | Technology |
| :--- | :--- |
| Language | Python 3.13 |
| Backend / API | FastAPI + Uvicorn |
| Database | SQLite (built-in `sqlite3`) + FTS5 full-text search |
| Serverless adapter | Mangum (Vercel / AWS Lambda) |
| Frontend | Vanilla JS, Tailwind CSS (CDN), Font Awesome (CDN) |
| Hosting | Render (primary) · Vercel (secondary) |
| Source control | GitHub |

---

## 💻 Local Quickstart

### 1. Clone and install

```bash
git clone https://github.com/stackvector/credBase.git
cd credBase
pip install -r requirements.txt
```

### 2. Run

```bash
python app.py
```

Or with uvicorn directly:

```bash
uvicorn app:app --reload --port 8000
```

### 3. Open

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

> The database (`credentials.db`) is already committed to the repo with 1,393 cleaned and indexed records — no import step needed.

---

## 📡 API Reference

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/` | `GET` | Serves the web UI |
| `/api/credentials` | `GET` | Search & filter (`q`, `type`, `level`, `duration_bracket`, `sort`, `page`, `page_size`) |
| `/api/credentials/{id}` | `GET` | Single credential detail |
| `/api/filters` | `GET` | Live facet counts for sidebar |
| `/api/stats` | `GET` | Catalog statistics |
| `/api/health` | `GET` | Health check |

---

## 🚀 Deployment

### Render (Recommended for SQLite)

1. Connect your GitHub repo on [render.com](https://render.com) → **New Web Service**
2. Set:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
3. Deploy — live at your free `https://<app>.onrender.com` URL.

The included `Procfile` handles this automatically if you use Render's Git-based deploys.

### Vercel (Serverless)

The repo includes a `vercel.json` and the app exports a `handler = Mangum(app)` entry point.

1. Import the GitHub repo at [vercel.com/new](https://vercel.com/new), or run:
   ```bash
   npm i -g vercel
   vercel
   ```
2. No extra config needed — Vercel picks up `vercel.json` automatically.

---

## 📁 Project Structure

```
credBase/
├── app.py                 # FastAPI backend (API + static serving)
├── static/
│   └── index.html         # Single-page frontend (Tailwind + Vanilla JS)
├── credentials.db         # SQLite database — 1,393 records + FTS5 index
├── catalog.json           # Raw catalog from Google Skills API (Phase 1)
├── enriched_10.json       # AI enrichment sample (10 records)
├── collect_catalog.py     # Phase 1 — catalog scraper
├── import_catalog.py      # Phase 2 — JSON → SQLite importer
├── clean_catalog.py       # Phase 3B — data cleaning pipeline
├── enrich_10_samples.py   # Phase 4A — Gemini AI enrichment sample
├── requirements.txt
├── Procfile               # Render start command
├── vercel.json            # Vercel serverless config
└── .gitignore
```

---

## 📊 Database Stats

| Metric | Count |
| :--- | ---: |
| Total records | 1,393 |
| Labs | 688 |
| Courses | 612 |
| Learning Paths | 93 |
| Introductory | 792 |
| Intermediate | 423 |
| Advanced | 71 |
