import requests

def ensure_etl_tag(token_medusa, base_url):
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token_medusa['token']}",
        "Content-Type": "application/json"
    })
    get_url = f"{base_url}/admin/product-tags"
    resp = session.get(get_url)
    if resp.status_code != 200:
        raise Exception(f"Không lấy được danh sách tag: {resp.text}")
    tags = resp.json().get("product_tags", [])
    for tag in tags:
        if tag["value"] == "etl_migration":
            return tag["id"]
    create_url = f"{base_url}/admin/product-tags"
    create_resp = session.post(create_url, json={"value": "etl_migration"})
    if create_resp.status_code != 200:
        raise Exception(f"Không tạo được tag: {create_resp.text}")
    tag_id = create_resp.json()["product_tag"]["id"]
    return tag_id