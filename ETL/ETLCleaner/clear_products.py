import requests


class CleanupProducts:

    def __init__(self, token_medusa, base_url):
        self.base_url = base_url
        self.token_medusa = token_medusa["token"]

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token_medusa}",
            "Content-Type": "application/json"
        })

    def clear_products(self, tag="etl_migration"):
        url = f"{self.base_url}/admin/products?limit=200"
        resp = self.session.get(url)
        if resp.status_code != 200:
            raise Exception(resp.text)
        products = resp.json().get("products", [])
        count = 0
        for product in products:
            tags = [t["value"] for t in product.get("tags", [])]
            if tag in tags:
                product_id = product["id"]
                del_url = f"{self.base_url}/admin/products/{product_id}"
                del_resp = self.session.delete(del_url)
