import sqlite3
import json

import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect(os.path.join(ROOT_DIR, "credentials.db"))
cursor = conn.cursor()

# Select 10 diverse sample records across types (course, lab, path) and topics
cursor.execute("""
    SELECT id, title, description, type, level, duration_minutes, url
    FROM credentials
    WHERE id IN (
        'course_templates_783',   -- Manage Kubernetes in Google Cloud (course)
        'course_templates_623',   -- Derive Insights from BigQuery Data (course)
        'focuses_49746',          -- Using BigQuery Omni with AWS (lab)
        'focuses_23118',          -- BigQuery Soccer Data Analysis (lab)
        'course_templates_746',   -- Managing Cloud Infrastructure with Terraform (course)
        'course_templates_536',   -- Introduction to Generative AI (course)
        'course_templates_927',   -- Machine Learning Operations (MLOps) for Generative AI (course)
        'paths_3135',             -- Google DeepMind: AI Research Foundations (path)
        'course_templates_1197',  -- SecOps on GDC for Tier 3 Analysts (course)
        'course_templates_1430'   -- Network Observability on Google Cloud (course)
    )
    ORDER BY id
""")

rows = cursor.fetchall()
conn.close()

samples = []
for r in rows:
    samples.append({
        "id": r[0],
        "title": r[1],
        "description": r[2],
        "type": r[3],
        "level": r[4],
        "duration_minutes": r[5],
        "url": r[6]
    })

print(f"Selected {len(samples)} diverse records for Phase 4A testing:")
for idx, s in enumerate(samples, 1):
    print(f"{idx}. [{s['id']}] {s['title']} ({s['type']} | {s['level'] or 'unspecified'})")

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples_10.json"), "w", encoding="utf-8") as f:
    json.dump(samples, f, indent=2, ensure_ascii=False)
