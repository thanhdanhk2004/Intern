import yaml
import requests
import time
import pprint

from ETLOrder.mapping_order import Mapping
from ETLOrder.transformer import Transformer
from ETLOrder.validator import Validate, write_dlq
from ETL.DataExtractLayer.Order import OrderMagento


with open("Mapper/mapping_order.yaml", encoding="utf-8") as f:
    mapper_order = yaml.safe_load(f)


class PipelineOrder:

    def __init__(self, *, token_medusa, token_magento,
                 magento_base_url, medusa_base_url,
                 retry=30, timeout=5):

        self.token_medusa = token_medusa
        self.retry = retry
        self.timeout = timeout

        self.region_id = None
        self.shipping_option_id = None
        self.shipping_option_name = None

        self.extractor = OrderMagento(
            base_url=magento_base_url,
            token=token_magento
        )

        self.mapping = Mapping()
        self.transformer = Transformer()
        self.validator = Validate()

        self.medusa_base_url = medusa_base_url.rstrip("/")

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token_medusa}",
            "Content-Type": "application/json"
        })
    def fetch_regions(self):
        res = self.session.get(f"{self.medusa_base_url}/admin/regions", timeout=self.timeout)
        res.raise_for_status()
        return res.json().get("regions", [])

    def resolve_region_id(self, currency_code=None):
        regions = self.fetch_regions()
        if not regions:
            raise Exception("No regions found in Medusa")
        if currency_code:
            for r in regions:
                if r.get("currency_code") == currency_code.lower():
                    return r["id"]
        return regions[0]["id"]

    def resolve_shipping_option(self):
        if self.shipping_option_id:
            return
        res = self.session.get(f"{self.medusa_base_url}/admin/shipping-options", timeout=self.timeout)
        res.raise_for_status()
        options = res.json().get("shipping_options", [])
        if not options:
            raise Exception("No shipping option found")
        opt = options[0]
        self.shipping_option_id = opt["id"]
        self.shipping_option_name = opt.get("name", "Standard Shipping")

    def fetch_customer_id(self, email):
        res = self.session.get(f"{self.medusa_base_url}/admin/customers?q={email}", timeout=self.timeout)
        res.raise_for_status()
        customers = res.json().get("customers", [])
        if not customers:
            raise Exception(f"Customer not found: {email}")
        return customers[0]["id"]

    def resolve_variant_id(self, sku):
        res = self.session.get(f"{self.medusa_base_url}/admin/variants?q={sku}", timeout=self.timeout)
        if res.status_code == 404:
            return "variant_01KBH2D2ZE7CZ61JR8FNT68SEA"
        res.raise_for_status()
        variants = res.json().get("variants", [])
        if not variants:
            return "variant_01KBH2D2ZE7CZ61JR8FNT68SEA"
        return variants[0]["id"]

    def create_draft_order(self, payload):
        res = self.session.post(f"{self.medusa_base_url}/admin/draft-orders", json=payload, timeout=self.timeout)
        res.raise_for_status()
        return res.json()["draft_order"]

    def convert_draft_order(self, draft_order_id):
        res = self.session.post(f"{self.medusa_base_url}/admin/draft-orders/{draft_order_id}/convert-to-order", timeout=self.timeout)
        res.raise_for_status()
        return res.json()["order"]

    def create_payment_collection(self, order_id, amount):
        res = self.session.post(
            f"{self.medusa_base_url}/admin/payment-collections",
            json={
                "order_id": order_id,
                "amount": int(amount)
            },
            timeout=self.timeout
        )
        res.raise_for_status()
        return res.json()["payment_collection"]

    def mark_paid(self, order_id, payment_collection_id):
        res = self.session.post(f"{self.medusa_base_url}/admin/mark-paid",
            json={
                "order_id": order_id,
                "payment_collection_id": payment_collection_id
            },
            timeout=self.timeout
        )
        res.raise_for_status()

    def capture_payment(self, payment_id):
        res = self.session.post(f"{self.medusa_base_url}/admin/payments/{payment_id}/capture", timeout=self.timeout)
        res.raise_for_status()

    def run(self, page_size=50, page=1, from_date=None):
        raw = self.extractor.load_orders(page_size=page_size, current_page=page, from_date=from_date)
        orders = raw.get("items", [])
        for order in orders:
            try:
                canonical = self.mapping.map_field_order(mapper_order, order)
                canonical = self.transformer.transform_all(canonical, self)
                if not self.region_id:
                    self.region_id = self.resolve_region_id(canonical.get("currency", "usd"))
                self.resolve_shipping_option()
                customer_id = self.fetch_customer_id(canonical["customer_email"])
                billing = order.get("billing_address", {})
                shipping_assign = order.get("extension_attributes", {}) \
                    .get("shipping_assignments", [{}])[0]
                shipping = shipping_assign.get("shipping", {}) \
                    .get("address", billing)

                def format_address(addr):
                    street = addr.get("street", [])
                    street_str = " ".join(street) if isinstance(street, list) else street
                    return {
                        "first_name": addr.get("firstname", ""),
                        "last_name": addr.get("lastname", ""),
                        "address_1": street_str,
                        "city": addr.get("city", ""),
                        "country_code": (addr.get("country_id") or "").lower(),
                        "postal_code": addr.get("postcode", ""),
                        "phone": addr.get("telephone", "")
                    }

                items = []
                for li in canonical["line_items"]:
                    variant_id = self.resolve_variant_id(li["sku"])
                    items.append({
                        "variant_id": variant_id,
                        "quantity": li["quantity"]
                    })
                draft_payload = {
                    "region_id": self.region_id,
                    "customer_id": customer_id,
                    "email": canonical["customer_email"],
                    "items": items,
                    "shipping_methods": [{
                        "shipping_option_id": self.shipping_option_id,
                        "name": self.shipping_option_name,
                        "amount": int(canonical.get("shipping_fee", 0)),
                        "data": {}
                    }],
                    "billing_address": format_address(billing),
                    "shipping_address": format_address(shipping),
                    "metadata": canonical.get("metadata", {})
                }
                pprint.pprint(draft_payload)
                draft = self.create_draft_order(draft_payload)
                order_medusa = self.convert_draft_order(draft["id"])
                pay_col = self.create_payment_collection(order_medusa["id"], canonical["total"])
                self.mark_paid(order_medusa["id"], pay_col["id"])
                payment_id = pay_col["payments"][0]["id"]
                self.capture_payment(payment_id)
            except Exception as e:
                write_dlq(order, str(e), level="order")