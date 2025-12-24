import json
import pprint

def write_dlq(item, reason, level="order", order_id=None, line_item_id=None):
    payload = {
        "level": level,
        "reason": reason,
        "order_id": order_id,
        "line_item_id": line_item_id,
        "item": item
    }

    print(f"[DLQ][{level.upper()}] {reason} (order: {order_id}, item: {line_item_id})")
    pprint.pprint(item)

    with open("dlq.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

class Validate:
    require_order_item_field = [
        "title",
        "quantity",
        "unit_price"
    ]

    def validate_order(self, order):
        items = order.get("line_items", [])
        if not items or not isinstance(items, list):
            write_dlq(order, "Order has no line_items", level="order")
            return False
        valid_items = []
        for item in items:
            if self.validate_order_item(item):
                valid_items.append(item)
        if not valid_items:
            write_dlq(order, "All order items are invalid", level="order")
            return False
        order["line_items"] = valid_items
        return True

    def validate_order_item(self, item):
        valid = True
        for field in self.require_order_item_field:
            if field not in item or item[field] in (None, "", 0):
                write_dlq(item, f"Missing order item field: {field}", level="order_item")
                valid = False
        if item.get("quantity", 0) <= 0:
            write_dlq(item, "Quantity must be > 0", level="order_item")
            valid = False
        if item.get("unit_price", 0) <= 0:
            write_dlq(item, "Unit price must be > 0", level="order_item")
            valid = False
        return valid