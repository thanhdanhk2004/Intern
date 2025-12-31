import json


def write_dql(item, reason, level="customer"):
    with open("dlq_customer.json", "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "level": level,
            "reason": reason,
            "item": item
        }, ensure_ascii=False) + "\n")


class ValidateCustomer:
    require_customer_filed = ["first_name", "last_name", "email"]
    require_address_filed = ["address_name", "city", "first_name", "last_name", "postal_code", "phone"]

    def validate_field_customer(self, customer):
        for field in self.require_customer_filed:
            if field not in customer:
                write_dql(customer, f"Missing field {field} in customer")
                return False
        return True

    def validate_field_address(self, address):
        for field in self.require_address_filed:
            if field not in address:
                write_dql(address, f"Missing field {field} in customer")
                return False
        return True
