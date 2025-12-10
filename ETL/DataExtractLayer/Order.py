from http.client import responses

import requests
import time

class OrderMagento:
    def __init__(self, base_url, token, timeout=20, retry=3):
        self.base_url = base_url
        self.token = token
        self.timeout = timeout
        self.retry = retry

        self.session = requests.session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        })

    def _request(self, endpoint):
        url = f"{self.base_url}/rest/default/V1/{endpoint}"

        for i in range(self.retry):
            response = self.session.get(url, timeout=self.timeout, verify=False)

            if response.status_code == 429:
                print("Please wait")
                time.sleep(1)
                continue

            if response.status_code >= 400:
                raise Exception(f"Error {response.status_code}: {response.text}")
            return response.json()
        raise Exception("Request failed after retries")

    def load_orders(self, page_size, page_current):
        endpoint = f"orders?searchCriteria[pageSize]={page_size}&searchCriteria[currentPage]={page_current}"
        return self._request(endpoint)

    def load_order_by_id(self, id_order):
        endpoint = f"orders/{id_order}"
        return self._request(endpoint)