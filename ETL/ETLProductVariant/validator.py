import json
def write_dql(item, reason, level="variant"):
    with open("dlq_product_variant.json", "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "level": level,
            "reason": reason,
            "item": item
        }, ensure_ascii=False) + "\n")

class ValidateVariant:
    require_variant_field = ['sku', 'title', 'prices', 'options']

    def validate_variant(self, product):
        for field in self.require_variant_field:
            if not product.get(field):
                write_dql(product, f"Missing variant field {field}")
                return False
        return True
