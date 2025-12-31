import requests


class CleanupCategories:
    def __init__(self, token_medusa, base_url):
        self.base_url = base_url
        self.token = token_medusa["token"]

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        })

    def clear_categories(self):
        url = f"{self.base_url}/admin/product-categories"
        resp = self.session.get(url)

        if resp.status_code != 200:
            raise Exception(f"Lỗi lấy danh sách category: {resp.text}")

        categories = resp.json().get("product_categories", [])
        deleted = 0

        for category in categories:
            if category is None:
                continue

            metadata = category.get("metadata") or {}

            if metadata.get("etl_migration") is True:
                cat_id = category["id"]
                delete_url = f"{self.base_url}/admin/product-categories/{cat_id}"

                del_resp = self.session.delete(delete_url)
        return deleted
