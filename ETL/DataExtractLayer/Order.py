from http.client import responses

import requests
import time


class OrderMagento:
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
        for attempt in range(self.retry):
            response = self.session.get(url, timeout=self.timeout, verify=False)
            if response.status_code == 429:
                print("Hit rate limit, retrying...")
                time.sleep(1)
                continue
            if response.status_code >= 400:
                raise Exception(f"Error {response.status_code}: {response.text}")
            return response.json()
        raise Exception("Request failed after retries")

    def load_orders(self, page_size=50, current_page=1, from_date=None):
        endpoint = f"orders?searchCriteria[pageSize]={page_size}&searchCriteria[currentPage]={current_page}"
        if from_date:
            # Thêm filter updated_at >= from_date
            endpoint += f"&searchCriteria[filterGroups][0][filters][0][field]=updated_at"
            endpoint += f"&searchCriteria[filterGroups][0][filters][0][value]={from_date}"
            endpoint += "&searchCriteria[filterGroups][0][filters][0][conditionType]=gteq"
        return self._request(endpoint)

    def load_order_by_id(self, order_id):
        endpoint = f"orders/{order_id}"
        return self._request(endpoint)

    def load_order_by_increment_id(self, increment_id):
        endpoint = f"orders?searchCriteria[filterGroups][0][filters][0][field]=increment_id" \
                   f"&searchCriteria[filterGroups][0][filters][0][value]={increment_id}" \
                   f"&searchCriteria[filterGroups][0][filters][0][conditionType]=eq"
        data = self._request(endpoint)
        items = data.get("items", [])
        return items[0] if items else None
