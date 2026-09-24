# Google Skills Finder 🚀

A modern, fast web application and API to search, filter, and discover **1,390+ official Google Cloud credentials**, hands-on labs, skill badge courses, and learning paths.

---

## 🌟 Key Features (V1)

- **⚡ Lightning-Fast Full-Text Search**: Uses SQLite FTS5 (Full-Text Search) with prefix and multi-keyword matching over course titles and descriptions.
- **🎯 Multi-Faceted Filters**:
  - **Credential Type**: Hands-on Lab (688), Skill Course (612), Learning Path (93).
  - **Difficulty Level**: Introductory (792), Intermediate (423), Advanced (71), Unspecified (107).
  - **Duration**: Quick (&le; 30 min), Short (&le; 1 hour), Medium (1–3 hours), Deep Dive (&gt; 3 hours).
  - **AI Enriched**: Filter for credentials with curated target technical skills and career paths.
- **🔄 Instant Sorting**: Sort by Relevance, Title (A-Z / Z-A), Shortest Duration, or Longest Duration.
- **📱 Clean Google-Inspired UI**: Responsive, sleek desktop and mobile design with Tailwind CSS.
- **🔍 Quick View Modal**: Preview details, estimated time, and skills without navigating away.
- **🔗 Direct Canonical Links**: One-click launcher into official Google Skills pages.
- **🌐 Shareable URLs**: State is synchronized to URL query parameters (`?q=Kubernetes&level=intermediate`).

---

## 💻 Local Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```
Or with uvicorn:
```bash
uvicorn app:app --reload --port 8000
```

### 3. Open in Browser
Visit [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 📡 API Endpoints

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/` | `GET` | Serves the web UI |
| `/api/credentials` | `GET` | Search & filter credentials (`q`, `type`, `level`, `duration_bracket`, `sort`, `page`) |
| `/api/credentials/{id}` | `GET` | Get single credential detail |
| `/api/filters` | `GET` | Dynamic facet counts for sidebar |
| `/api/stats` | `GET` | Catalog statistics |
| `/api/health` | `GET` | API health check |

---

## 🚀 Deployment Instructions

### Option 1: Deploy on Render.com (Recommended for SQLite)
Render provides a completely free tier for Python web services and works with SQLite out of the box.

1. Push this project folder to a GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Initial Google Skills Finder V1"
   git branch -M main
   git remote add origin https://github.com/<your-username>/google-skills-finder.git
   git push -u origin main
   ```
2. Go to [render.com](https://render.com) and create an account.
3. Click **New +** &rarr; **Web Service**.
4. Connect your GitHub repository.
5. Set:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
6. Click **Deploy Web Service**. Done! Your app is live with a free `https://<app>.onrender.com` URL.

---

### Option 2: Deploy on Vercel
Vercel allows running FastAPI via serverless functions.

1. Install the Vercel CLI:
   ```bash
   npm i -g vercel
   ```
2. Run in the project directory:
   ```bash
   vercel
   ```
3. Follow the prompts (Select default settings). The included `vercel.json` and `app.py` handle serverless routing automatically.
4. Alternatively, import your GitHub repository into the [Vercel Dashboard](https://vercel.com/new).
