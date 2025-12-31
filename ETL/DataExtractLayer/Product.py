from http.client import responses

import requests
import time


class ProductMagento:
    def __init__(self, base_url, token, timeout=50, retry=3):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.retry = retry

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        })

    def _request(self, endpoint):
        url = f"{self.base_url}/rest/default/V1/{endpoint}"

        for attemp in range(self.retry):
            response = self.session.get(url, timeout=self.timeout, verify=False)

            if response.status_code == 429:
                print("Hit rate limit, retrying...")
                time.sleep(1)
                continue

            if response.status_code >= 400:
                raise Exception(f"Error {response.status_code}: {response.text}")

            return response.json()
        raise Exception("Request failed after retries")

    def get_products(self, page_size=10, current_page=1):
        endpoint = f"products?searchCriteria[pageSize]={page_size}&searchCriteria[currentPage]={current_page}"
        return self._request(endpoint)

    def get_product_by_sku(self, sku):
        endpoint = f"products/{sku}"
        return self._request(endpoint)

    def get_children(self, sku):  # CAMTU
        endpoint = f"configurable-products/{sku}/children"
        return self._request(endpoint)
