import json
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Define enriched metadata for the 10 Phase 4A sample records
enrichments = {
    "course_templates_1197": {
        "summary": "Advanced security operations training for Tier 3 SOC analysts working on Google Distributed Cloud environments.",
        "skills": ["Security Operations", "Incident Response", "GDC (Google Distributed Cloud)", "Threat Analysis", "SIEM"],
        "domains": ["Cybersecurity", "Cloud Security"],
        "career_paths": ["Security Analyst", "SOC Tier 3 Analyst", "Cybersecurity Specialist"]
    },
    "course_templates_1430": {
        "summary": "Learn to monitor, diagnose, and optimize Google Cloud network traffic and telemetry using native observability tools.",
        "skills": ["Network Observability", "Packet Mirroring", "VPC Flow Logs", "Network Intelligence Center", "Cloud Monitoring"],
        "domains": ["Cloud Networking", "DevOps & SRE"],
        "career_paths": ["Cloud Network Engineer", "SRE (Site Reliability Engineer)", "Cloud Architect"]
    },
    "course_templates_536": {
        "summary": "Foundational course introducing Generative AI concepts, LLM architecture, and Google's Generative AI ecosystem.",
        "skills": ["Generative AI", "Large Language Models", "Prompting Concepts", "Responsible AI", "Google AI Tools"],
        "domains": ["Artificial Intelligence", "Machine Learning"],
        "career_paths": ["AI Product Manager", "AI Application Developer", "Data Scientist"]
    },
    "course_templates_623": {
        "summary": "Skill badge course covering SQL querying, public dataset exploration, syntax troubleshooting, and Looker Studio reporting in BigQuery.",
        "skills": ["SQL", "BigQuery", "Data Visualization", "Looker Studio", "Data Analysis", "Query Optimization"],
        "domains": ["Data Analytics", "Cloud Data Warehousing"],
        "career_paths": ["Data Analyst", "Business Intelligence Analyst", "Data Engineer"]
    },
    "course_templates_746": {
        "summary": "Comprehensive course on automating and managing Google Cloud infrastructure using HashiCorp Terraform.",
        "skills": ["Terraform", "Infrastructure as Code (IaC)", "HCL", "GCP Resource Provisioning", "Terraform State Management"],
        "domains": ["Cloud DevOps", "Infrastructure Engineering"],
        "career_paths": ["DevOps Engineer", "Cloud Engineer", "Infrastructure Architect"]
    },
    "course_templates_783": {
        "summary": "Skill badge course covering GKE deployment scaling, kubectl application debugging, and metric collection using Managed Prometheus.",
        "skills": ["Kubernetes", "GKE (Google Kubernetes Engine)", "kubectl", "Container Management", "Continuous Delivery", "Prometheus"],
        "domains": ["Containerization & Orchestration", "Cloud DevOps"],
        "career_paths": ["Kubernetes Engineer", "DevOps Engineer", "Cloud Infrastructure Engineer"]
    },
    "course_templates_927": {
        "summary": "Practice operationalizing, deploying, and monitoring Generative AI models using MLOps best practices on Google Cloud.",
        "skills": ["MLOps", "Model Deployment", "Model Monitoring", "Vertex AI", "Generative AI Pipelines", "CI/CD for ML"],
        "domains": ["Machine Learning Engineering", "AI Operations"],
        "career_paths": ["MLOps Engineer", "Machine Learning Engineer", "AI Infrastructure Engineer"]
    },
    "focuses_23118": {
        "summary": "Hands-on lab writing complex SQL queries and joins on BigQuery tables to derive statistical insights from soccer match events.",
        "skills": ["SQL Joins", "BigQuery", "Data Aggregation", "Sports Analytics", "SAFE_DIVIDE", "UNNEST"],
        "domains": ["Data Analytics", "SQL Data Engineering"],
        "career_paths": ["Data Analyst", "Sports Analytics Specialist", "SQL Developer"]
    },
    "focuses_49746": {
        "summary": "Advanced lab configuring BigQuery Omni to query data residing in AWS S3 without data egress or cross-cloud migration.",
        "skills": ["BigQuery Omni", "Multi-Cloud Analytics", "AWS S3 Integration", "Cross-Cloud Querying", "Cloud IAM"],
        "domains": ["Multi-Cloud Architecture", "Data Engineering"],
        "career_paths": ["Cloud Data Architect", "Multi-Cloud Engineer", "Principal Data Engineer"]
    },
    "paths_3135": {
        "summary": "Learning path covering foundational research topics, model architectures, and core principles from Google DeepMind.",
        "skills": ["Deep Learning", "Neural Networks", "AI Research Methodologies", "TensorFlow / JAX", "Transformers"],
        "domains": ["AI Research", "Deep Learning"],
        "career_paths": ["AI Research Scientist", "Machine Learning Researcher", "Deep Learning Engineer"]
    }
}

samples_file = os.path.join(CURRENT_DIR, "samples_10.json")
with open(samples_file, "r", encoding="utf-8") as f:
    samples = json.load(f)

enriched_output = []
for item in samples:
    item_id = item["id"]
    enrichment = enrichments.get(item_id, {})
    
    enriched_item = {
        "id": item["id"],
        "title": item["title"],
        "type": item["type"],
        "level": item["level"],
        "duration_minutes": item["duration_minutes"],
        "url": item["url"],
        "description": item["description"],
        "enrichment": {
            "summary": enrichment.get("summary", ""),
            "skills": enrichment.get("skills", []),
            "domains": enrichment.get("domains", []),
            "career_paths": enrichment.get("career_paths", [])
        }
    }
    enriched_output.append(enriched_item)

output_file = os.path.join(CURRENT_DIR, "enriched_10.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(enriched_output, f, indent=2, ensure_ascii=False)

print(f"Successfully generated Phase 4A enriched dataset for 10 records in '{output_file}'.")
