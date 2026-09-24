import json
from app import health_check, get_stats, get_filters, list_credentials, get_credential

def test_direct():
    # 1. Health check
    h = health_check()
    print("1. Health check:", h)
    assert h["status"] == "ok"
    assert h["total_records"] == 1393

    # 2. Stats
    s = get_stats()
    print("2. Stats:", s)
    assert s["total"] == 1393

    # 3. Filters
    f = get_filters()
    print("3. Filters:", f)
    assert f["types"]["lab"] > 0

    # 4. Search credentials
    res = list_credentials(q="Kubernetes", level="intermediate", page=1, page_size=10)
    print(f"4. Search 'Kubernetes': Total={res['total']}, returned={len(res['items'])}")
    assert res["total"] > 0
    assert len(res["items"]) <= 10

    # 5. Get single credential
    cred_id = res["items"][0]["id"]
    single = get_credential(cred_id)
    print(f"5. Credential ({cred_id}): {single['title']} | duration={single['duration']}")
    assert single["id"] == cred_id

    # 6. Filter by AI enriched
    enr = list_credentials(enriched_only=True)
    print(f"6. AI Enriched only: Total={enr['total']}")
    assert enr["total"] == 10

    print("\nAll direct API tests passed successfully!")

if __name__ == "__main__":
    test_direct()
