import json
import logging
import urllib.parse
import requests

BASE_URL = "https://www.skills.google/catalog/list"
DOMAIN = "https://www.skills.google"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def build_full_url(path: str) -> str:
    """Converts relative catalog item path to full Google Skills URL."""
    if not path:
        return ""
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return urllib.parse.urljoin(DOMAIN, path)

def fetch_catalog() -> list[dict]:
    """Fetches all items from the Google Skills catalog endpoint using pagination."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    })

    page = 1
    per_page = 50
    records = []

    logging.info("Starting Google Skills catalog fetch...")

    while True:
        params = {
            "page": page,
            "per_page": per_page
        }
        
        try:
            response = session.get(BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            items = data if isinstance(data, list) else data.get("catalog", [])
            
            if not items:
                logging.info(f"Page {page} returned 0 items. Reached end of catalog pagination.")
                break

            for item in items:
                relative_path = item.get("path") or ""
                full_url = build_full_url(relative_path)
                
                record = {
                    "title": item.get("title") or "",
                    "description": item.get("description") or "",
                    "duration": item.get("duration") or "",
                    "url": full_url,
                    "type": item.get("type") or "",
                    "level": item.get("level") or "",
                    "paid": bool(item.get("paid")) if item.get("paid") is not None else False
                }
                records.append(record)

            logging.info(f"Page {page}: fetched {len(items)} items (Total collected: {len(records)})")
            page += 1

        except requests.RequestException as exc:
            logging.error(f"HTTP request error on page {page}: {exc}")
            break

    logging.info(f"Catalog fetch complete. Total items fetched: {len(records)}")
    return records

def main():
    catalog_items = fetch_catalog()
    output_filename = "catalog.json"
    
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(catalog_items, f, indent=2, ensure_ascii=False)
        
    logging.info(f"Saved {len(catalog_items)} records into '{output_filename}' using UTF-8.")

if __name__ == "__main__":
    main()
