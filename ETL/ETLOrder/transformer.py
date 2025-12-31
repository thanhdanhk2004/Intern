import uuid
from datetime import datetime


class Transformer:
    def transform_money(self, order):
        money_fields = ["subtotal", "tax", "shipping_fee", "total"]
        for field in money_fields:
            if order.get(field) is None:
                order[field] = 0
            order[field] = int(order[field] * 100) if isinstance(order[field], float) else int(order[field])

    def transform_line_items(self, order):
        for item in order.get("line_items", []):
            if not item.get("total"):
                item["total"] = item["unit_price"] * item["quantity"]
            item["unit_price"] = int(item["unit_price"])
            item["quantity"] = int(item["quantity"])
            item["total"] = int(item["total"])

    def transform_totals(self, order):
        subtotal = sum([li["total"] for li in order["line_items"]])
        tax = order.get("tax", 0)
        shipping_fee = order.get("shipping_fee", 0)
        order["subtotal"] = subtotal
        order["total"] = subtotal + tax + shipping_fee

    def transform_payment_full(self, order):
        payment = order.get("payment")
        if payment:
            order["payments"] = [{
                "provider": payment.get("provider"),
                "amount": payment.get("amount"),
                "data": payment.get("metadata", {}),
                "txn_id": payment.get("txn_id")
            }]
        else:
            order["payments"] = []
        if "payment" in order:
            del order["payment"]

    def transform_status(self, order):
        if not order.get("status"):
            order["status"] = "pending"

    def transform_metadata(self, order):
        order["metadata"] = {
            "source": "magento",
            "magento_order_id": order.get("id"),
            "customer_email": order.get("customer_email"),
            "migration_timestamp": datetime.utcnow().isoformat()
        }

    def checksum(self, order):
        for item in order["line_items"]:
            if item["quantity"] * item["unit_price"] != item["total"]:
                raise Exception(f"Line item invalid: {item}")
        return order

    def to_medusa_customer_items(self, line_items_list):
        items_medusa = []
        for item in line_items_list:
            sku = item.get("sku")
            if not sku:
                raise Exception(f"Order item missing SKU: {item}")
            items_medusa.append({
                "title": item.get("title"),
                "unit_price": item["unit_price"],
                "quantity": item["quantity"],
                "metadata": {
                    "sku": sku,
                    "magento_item_id": item.get("item_id")
                }
            })
        return items_medusa

    def transform_all(self, order, pipeline):
        self.transform_money(order)
        self.transform_line_items(order)
        order["line_items_medusa"] = self.to_medusa_customer_items(order["line_items"])
        self.transform_payment_full(order)
        self.transform_status(order)
        self.transform_metadata(order)
        self.checksum(order)
        return order
