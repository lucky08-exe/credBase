import os
import sys

# Ensure repository root is on sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app import health_check, get_stats, get_filters, list_credentials, get_credential, serve_index, serve_catalogue, serve_paths, serve_path_detail

def test_direct():
    # 0. Frontend routing tests
    idx = serve_index()
    assert os.path.exists(idx.path)
    cat = serve_catalogue()
    assert os.path.exists(cat.path)
    pts = serve_paths()
    assert os.path.exists(pts.path)
    p_detail = serve_path_detail("cloud-computing")
    assert os.path.exists(p_detail.path)
    # 1. Health check
    h = health_check()
    print("1. Health check:", h)
    assert h["status"] == "ok"
    assert h["total_records"] == 1393

    # 2. Stats
    s = get_stats()
    print("2. Stats:", s)
    assert s["total"] == 1393
    assert s["type_counts"]["lab"] > 0
    assert s["type_counts"]["course"] > 0
    assert s["type_counts"]["learning_path"] == 93

    # 3. Filters
    f = get_filters()
    print("3. Filters:", f)
    assert f["types"]["lab"] > 0
    assert f["types"]["learning_path"] == 93
    total_duration_brackets = (
        f["duration_brackets"]["<30m"] +
        f["duration_brackets"]["<1h"] +
        f["duration_brackets"]["1-3h"] +
        f["duration_brackets"][">3h"]
    )
    assert total_duration_brackets == h["total_records"]

    # 4. Search credentials
    res = list_credentials(q="Kubernetes", level="intermediate", page=1, page_size=10)
    print(f"4. Search 'Kubernetes': Total={res['total']}, returned={len(res['items'])}")
    assert res["total"] > 0
    assert len(res["items"]) <= 10

    # 4b. Learning paths and focus-lab URLs
    paths = list_credentials(type="learning_path", page=1, page_size=100)
    print(f"4b. Learning paths: Total={paths['total']}")
    assert paths["total"] == 93

    focus = get_credential("focuses_84417")
    assert "parent=catalog" in focus["url"]

    # 5. Get single credential
    cred_id = res["items"][0]["id"]
    single = get_credential(cred_id)
    print(f"5. Credential ({cred_id}): {single['title']} | duration={single['duration']}")
    assert single["id"] == cred_id

    # 6. Sorting
    sort_dur = list_credentials(sort="duration_asc", page=1, page_size=5)
    assert len(sort_dur["items"]) == 5
    assert sort_dur["items"][0]["duration_minutes"] is not None

    print("\nAll V1 direct API tests passed successfully!")

if __name__ == "__main__":
    test_direct()
