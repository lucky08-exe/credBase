# Google Skills Finder

[![Live App](https://img.shields.io/badge/Live_App-credbase.onrender.com-1a73e8?style=flat-square&logo=google-cloud&logoColor=white)](https://credbase.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLite](https://img.shields.io/badge/SQLite-FTS5_BM25-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://www.sqlite.org/fts5.html)
[![License](https://img.shields.io/badge/License-MIT-gray?style=flat-square)](#)

A fast, searchable discovery platform and REST API indexing **1,393 official Google Cloud credentials**, hands-on labs, skill courses, and multi-course learning paths.

🔗 **Production Application**: [credbase.onrender.com](https://credbase.onrender.com)

---

## 💡 Overview

Google Cloud's official skills ecosystem contains hundreds of hands-on labs, courses, and learning paths scattered across different categories and difficulty levels. Finding specific credentials tailored to a learner's skill level, duration constraints, or career goals can be cumbersome.

**Google Skills Finder (credBase)** provides a unified catalog interface and high-performance search engine built specifically for Google Cloud training content. Powered by SQLite Full-Text Search (FTS5) with BM25 ranking, it delivers instantaneous search, multi-faceted filtering, and direct links into Google Cloud training environments.

---

## ✨ Features (V1 Release)

- **⚡ Full-Text Search Engine**: SQLite FTS5 prefix-matching and multi-keyword search with BM25 relevance ranking across course titles and descriptions.
- **🎯 Multi-Faceted Filters**:
  - **Credential Types**: Hands-on Labs (688), Skill Courses (612), Learning Paths (93).
  - **Difficulty Levels**: Introductory (792), Intermediate (423), Advanced (71), and Unspecified (107).
  - **Duration Brackets**: Quick (≤ 30 min), Short (31–60 min), Medium (1–3 hours), and Deep Dive (> 3 hours).
- **🔄 Flexible Sorting**: Sort results by Relevance, Duration (shortest to longest / longest to shortest), or Alphabetical Title (A–Z / Z–A).
- **🔍 Quick View Modal**: Inspect descriptions, durations, levels, and prerequisites in an overlay without losing search context or navigation state.
- **🔗 Direct Link Preservation**: Special handling for hands-on lab focus URLs (`/focuses/`) preserving required catalog context (`parent=catalog`) so labs launch directly into the active Google console.
- **🌐 Synchronized URL State**: Search terms, active filters, sorting preferences, and pagination are synchronized to URL query parameters (`?q=Kubernetes&level=intermediate`) for bookmarking and sharing.
- **📱 Responsive UI**: Google Cloud-inspired design built with Tailwind CSS, supporting desktop, tablet, and mobile browsers.

---

## 🏗️ Architecture & Tech Stack

```
credBase/
├── app.py                     # FastAPI backend (REST API & static file serving)
├── credentials.db             # SQLite database (1,393 records + FTS5 index)
├── static/
│   └── index.html             # Single-page frontend (Tailwind CSS, Vanilla JS)
├── pipeline/                  # Data engineering & cleaning pipeline
│   ├── collect_catalog.py     # Scrapes Google Skills catalog API
│   ├── import_catalog.py      # Ingests JSON catalog into SQLite
│   ├── clean_catalog.py       # Cleans URLs, normalizes durations and types
│   └── audit_data.py          # Data quality & schema auditor
├── tests/                     # Verification and test suites
│   ├── test_direct.py         # End-to-end API and search test suite
│   └── verify_phase2.py       # Database schema and integrity checks
├── v2_enrichment/             # V2 enrichment prototypes & sample datasets
│   ├── enriched_10.json       # 10 reference enriched course records
│   ├── samples_10.json        # Extracted benchmark samples
│   ├── enrich_10_samples.py   # Enrichment transformation generator
│   ├── select_10_samples.py   # Diverse sample query selector
│   └── extract_one.py         # Deep web scraper prototype for lab focus pages
├── docs/                      # Architectural & handoff specifications
│   └── V2_ENRICHMENT_HANDOFF.md # V2 Enrichment architecture and implementation plan
├── Procfile                   # Render production deployment configuration
├── vercel.json                # Vercel serverless deployment configuration
└── requirements.txt           # Python application dependencies
```

### Technology Highlights

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) | High-throughput asynchronous REST API with automatic OpenAPI documentation. |
| **Search & Database** | [SQLite FTS5](https://www.sqlite.org/fts5.html) | Zero-maintenance embedded database with native BM25 full-text indexing. |
| **Serverless Adapter** | [Mangum](https://mangum.io/) | ASGI adapter enabling dual deployment across standard containers (Render) and serverless environments (Vercel). |
| **Frontend** | Vanilla JS + [Tailwind CSS](https://tailwindcss.com/) | Ultra-fast load times, zero client build pipeline, and clean component styling. |
| **Production Host** | [Render](https://render.com/) | Persistent container deployment running Uvicorn with automated GitHub deploys. |

---

## 📡 REST API Reference

The backend exposes a public RESTful API powering the search experience:

### Endpoints

| Method | Endpoint | Description |
| :---: | :--- | :--- |
| `GET` | `/` | Serves the web application single-page interface. |
| `GET` | `/api/credentials` | Search, filter, sort, and paginate through catalog credentials. |
| `GET` | `/api/credentials/{id}` | Retrieve complete metadata for a single credential by identifier. |
| `GET` | `/api/filters` | Aggregated facet counts for active filters and duration brackets. |
| `GET` | `/api/stats` | High-level catalog statistics (total records, category counts, averages). |
| `GET` | `/api/health` | Health check endpoint returning database connectivity status and row counts. |

### Query Parameters for `/api/credentials`

| Parameter | Type | Default | Description |
| :--- | :---: | :---: | :--- |
| `q` | `string` | — | Search keywords matched against title and description using FTS5 BM25. |
| `type` | `string` | `all` | Filter by credential type: `lab`, `course`, `learning_path`, or comma-separated list. |
| `level` | `string` | `all` | Filter by difficulty level: `introductory`, `intermediate`, `advanced`, `unspecified`. |
| `duration_bracket` | `string` | `all` | Duration bucket: `<30m`, `<1h`, `1-3h`, `>3h`. |
| `sort` | `string` | `relevance` | Ordering: `relevance`, `duration_asc`, `duration_desc`, `title_asc`, `title_desc`. |
| `page` | `integer` | `1` | Page number for paginated results. |
| `page_size` | `integer` | `24` | Items per page (min: 1, max: 100). |

---

## 🚀 Roadmap: What's Next in V2?

With **V1** successfully deployed and serving the core catalog, the next major release (**V2**) will focus on **Deep Catalog Enrichment**:

1. **AI-Powered Skills Extraction**: Utilizing Gemini models to extract structured, granular skill tags (e.g. *Terraform*, *VPC Flow Logs*, *BigQuery UNNEST*, *MLOps*) across the entire 1,393-item catalog.
2. **Career Path Mapping**: Mapping courses and lab sequences to explicit cloud engineering career tracks (e.g., *DevOps Engineer*, *Security Analyst*, *Data Architect*).
3. **Prerequisite & Certification Alignment**: Showing prerequisites and linking courses directly to Google Cloud certification exams (e.g. *Professional Cloud Architect*, *Associate Cloud Engineer*).
4. **Relational Schema Migration**: Introducing dedicated `skills` and `career_paths` relational tables in SQLite for multi-skill filtering.

> For the complete technical specification, prototype code, and sample datasets, see the [V2 Enrichment Handoff Document](docs/V2_ENRICHMENT_HANDOFF.md).

---

## 📄 License

This project is licensed under the MIT License. Data sourced from official [Google Cloud Skills](https://www.skills.google) catalog listings.
