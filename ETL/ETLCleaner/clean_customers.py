import requests
import time

class CleanupCustomerData:
    def __init__(self, base_url, token_medusa, retry=5, timeout=5):
        self.base_url = base_url
        self.retry = retry
        self.timeout = timeout
        self.token_medusa = token_medusa["token"]

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token_medusa}",
            "Content-Type": "application/json"
        })

    def clear_customers(self):
        url = f"{self.base_url}/admin/customers"
        resp = self.session.get(url)
        if resp.status_code != 200:
            raise Exception(f"Cannot load customers: {resp.status_code} {resp.text}")
        customers = resp.json().get("customers", [])
        count = 0
        for customer in customers:
            # Không xoá admin hoặc người có quyền
            if "admin" in customer["email"].lower():
                continue
            customer_id = customer["id"]
            del_url = f"{self.base_url}/admin/customers/{customer_id}"
            for _ in range(self.retry):
                d = self.session.delete(del_url)

                if d.status_code == 200:
                    count += 1
                    break
                elif d.status_code == 429:
                    time.sleep(1)
                    continue
                else:
                    break

    def clear_customer_groups(self):
        url = f"{self.base_url}/admin/customer-groups"
        resp = self.session.get(url)
        if resp.status_code != 200:
            raise Exception(f"Cannot load customer groups: {resp.status_code} {resp.text}")
        groups = resp.json().get("customer_groups", [])
        count = 0
        for group in groups:
            name = group.get("name", "").lower()
            group_id = group["id"]
            del_url = f"{self.base_url}/admin/customer-groups/{group_id}"
            for _ in range(self.retry):
                d = self.session.delete(del_url)
                if d.status_code == 200:
                    count += 1
                    break
                elif d.status_code == 429:
                    time.sleep(1)
                    continue
                else:
                    break

    def clear_all(self):
        self.clear_customers()
        self.clear_customer_groups()