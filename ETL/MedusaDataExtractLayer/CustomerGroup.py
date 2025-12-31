import requests
import time


class CustomerGroupMedusa:
    def __init__(self, base_url, token, retry=5, time_out=60):
        self.base_url = base_url
        self.token = token
        self.retry = retry
        self.time_out = time_out

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        })

    def _request_add_customer_group(self, group_id, customer_id):
        if group_id is None or customer_id is None:
            return

        url = f"{self.base_url}/admin/customer-groups/{group_id}/customers"
        for i in range(self.retry):
            data = {"add": [customer_id]}
            response = self.session.post(url, json=data, timeout=self.time_out)

            if response.status_code == 429:
                print("Please wait")
                time.sleep(1)
                continue

            if response.status_code != 200:
                raise Exception(f"Add category failed: {response.status_code}: f{response.text}")

            return response.json()
        raise Exception("Add category failed")
