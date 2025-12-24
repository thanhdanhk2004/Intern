import json
with open("key.json", "r") as f:
    config = json.load(f)

class Mapping:
    def map_field_line_items(self, items):
        line_items = []
        for item in items:
            line_items.append({
                "sku": item.get("sku"),
                "title": item.get("name"),
                "unit_price": int(float(item.get("price", 0)) * 100),
                "quantity": int(item.get("qty_ordered", 0)),
                "total": int(float(item.get("row_total", 0)) * 100)
            })
        return line_items

    def map_field_payment(self, payment):
        if not payment:
            return None
        return {
            "provider": payment.get("method", "manual"),
            "amount": int(float(payment.get("amount_ordered", 0)) * 100),
            "txn_id": payment.get("last_trans_id") or payment.get("cc_trans_id")
        }

    def map_field_status(self, status):
        mapping = {
            "pending": "pending",
            "processing": "completed",
            "completed": "completed",
            "canceled": "canceled",
        }
        return mapping.get(status, "pending")

    def map_field_order(self, mapper, order):
        target_data = {}
        for canonical_field, magento_field in mapper["fields"].items():
            if canonical_field == "line_items":
                target_data["line_items"] = self.map_field_line_items(order.get(magento_field, []))
            elif canonical_field == "payment":
                target_data["payment"] = self.map_field_payment(order.get(magento_field))
            elif canonical_field == "status":
                target_data["status"] = self.map_field_status(order.get(magento_field))
            else:
                target_data[canonical_field] = order.get(magento_field)
        return target_data