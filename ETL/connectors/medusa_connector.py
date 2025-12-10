import time
import requests

class MedusaConnector:
    def __init__(self, base_url, token, time_out=20, retry=3):
        self.base_url = base_url
        self.token = token
        self.time_out = time_out
        self.retry = retry
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        })


    def get_data_product(self, magento_product):
        custom_attr = {attr["attribute_code"]: attr["value"] for attr in magento_product[0]["custom_attributes"]}

        medusa_data = {
            "title": magento_product[0]["name"],
            "description": custom_attr.get('description', ''),
            "handle": "long",
            "status": "published",
            "options": [
                {
                  "title": "Size",
                  "values": ["S", "M", "L"]
                }
              ],
            "thumbnail": magento_product[0]["media_gallery_entries"][0]["file"]
        }
        return medusa_data

    def add_product(self, magento_product):
        data_product = self.get_data_product(magento_product)
        if data_product is None:
            return
        url = f"{self.base_url}/admin/products"

        for i in range(self.retry):
            response = self.session.post(url, json=data_product, timeout=self.time_out)

            if response.status_code == 429:
                print("Please wait")
                time.sleep(1)
                continue

            if response.status_code >= 400:
                raise Exception(f"Error {response.status_code}: {response.text}")

            return response.json()
        raise Exception("Failed")