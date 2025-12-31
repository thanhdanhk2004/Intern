import yaml
import requests
from datetime import datetime

from ETLOrder.mapping_order import Mapping
from ETLOrder.transformer import Transformer
from ETLOrder.validator import write_dlq
from ETL.DataExtractLayer.Order import OrderMagento


with open("Mapper/mapping_order.yaml", encoding="utf-8") as f:
    mapper_order = yaml.safe_load(f)

class PipelineOrder:

    def __init__(self, *, token_medusa, token_magento,
                 magento_base_url, medusa_base_url,
                 timeout=10):
        self.timeout = timeout
        self.extractor = OrderMagento(
            base_url=magento_base_url,
            token=token_magento
        )
        self.mapping = Mapping()
        self.transformer = Transformer()
        self.medusa_base_url = medusa_base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token_medusa}",
            "Content-Type": "application/json"
        })

    def post(self, path, body=None):
        res = self.session.post(
            f"{self.medusa_base_url}{path}",
            json=body or {},
            timeout=self.timeout
        )
        if res.status_code >= 300:
            raise Exception(f"{path} {res.status_code}: {res.text}")
        return res.json()

    def get(self, path, params=None):
        res = self.session.get(
            f"{self.medusa_base_url}{path}",
            params=params,
            timeout=self.timeout
        )
        if res.status_code >= 300:
            raise Exception(f"{path} {res.status_code}: {res.text}")
        return res.json()

    def resolve_region(self, currency):
        regions = self.get("/admin/regions")["regions"]
        for r in regions:
            if r["currency_code"] == currency.lower():
                return r
        return regions[0]

    def resolve_shipping_option(self):
        return self.get("/admin/shipping-options")["shipping_options"][0]

    def resolve_customer(self, email):
        res = self.get("/admin/customers", {"q": email})
        if not res["customers"]:
            raise Exception(f"Customer not found {email}")
        return res["customers"][0]["id"]

    def run(self, page_size=50, page=1):
        raw = self.extractor.load_orders(
            page_size=page_size,
            current_page=page
        )
        for order in raw.get("items", []):
            inc_id = order.get("increment_id")
            try:
                canonical = self.mapping.map_field_order(mapper_order, order)
                canonical = self.transformer.transform_all(canonical, self)
                region = self.resolve_region(order.get("order_currency_code", "usd"))
                customer_id = self.resolve_customer(canonical["customer_email"])
                shipping_opt = self.resolve_shipping_option()
                items = []
                total_amount = 0
                for li in canonical["line_items"]:
                    price = float(li["unit_price"])
                    qty = int(li["quantity"])
                    total_amount += price * qty
                    items.append({
                        "title": li["title"],
                        "unit_price": price,
                        "quantity": qty
                    })
                shipping_amount = float(order.get("shipping_amount", 0))
                total_amount += shipping_amount
                billing = order.get("billing_address", {})

                def fmt(addr):
                    street = addr.get("street", [])
                    return {
                        "first_name": addr.get("firstname", ""),
                        "last_name": addr.get("lastname", ""),
                        "address_1": " ".join(street) if isinstance(street, list) else street,
                        "city": addr.get("city", ""),
                        "country_code": (addr.get("country_id") or "").lower(),
                        "postal_code": addr.get("postcode", ""),
                        "phone": addr.get("telephone", "")
                    }

                draft = self.post("/admin/draft-orders", {
                    "region_id": region["id"],
                    "customer_id": customer_id,
                    "email": canonical["customer_email"],
                    "items": items,
                    "shipping_methods": [{
                        "shipping_option_id": shipping_opt["id"],
                        "name": shipping_opt["name"],
                        "amount": shipping_amount
                    }],
                    "billing_address": fmt(billing),
                    "shipping_address": fmt(billing)
                })["draft_order"]
                draft_id = draft["id"]

                pay_col = self.post("/admin/payment-collections", {
                    "order_id": draft_id,
                    "amount": total_amount
                })["payment_collection"]

                payment = self.post("/admin/mark-paid", {
                    "order_id": draft_id,
                    "payment_collection_id": pay_col["id"]
                })
                payment_id = payment.get("id")
                if not payment_id:
                    raise Exception("No payment returned from mark-paid")

                self.post(f"/admin/payments/{payment_id}/capture")
                self.post(f"/admin/draft-orders/{draft_id}/convert")
            except Exception as e:
                write_dlq(order, str(e), level="order")