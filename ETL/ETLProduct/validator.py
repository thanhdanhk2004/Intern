import json
def write_dql(item, reason, level="product"):
    with open("dlq.json", "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "level": level,
            "reason": reason,
            "item": item
        }, ensure_ascii=False) + "\n")


class Validate:
    require_product_field = ['sku', 'title', 'amount']
    require_variant_field = ['sku', 'title', 'stock_quantity']

    def validate_product(self, product):
        for field in self.require_product_field:
            if not product.get(field):
                write_dql(product, f"Misssing product field {field}")
        return True



    def validate_quantity(self):
        if self.product["stock_quantity"] < 0:
            write_dql(self.product, f"Quantity smaller zero")
            return False
        return True

    def validate_price(self):
        if self.product["amount"] <= 0:
            write_dql(self.product, f"Price smaller zero")
            return False
        return True