import json


def write_dql(item, reason, level="category"):
    with open("dlq.json", "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "level": level,
            "reason": reason,
            "item": item
        }, ensure_ascii=False) + "\n")


class ValidatorCategory:
    require_filed_category = ['name', 'handle']

    def validate_categories(self, category):
        if not category:
            write_dql(category, "No category")
            return False
        for field in self.require_filed_category:
            if not category[field]:
                write_dql(category, f"Missing variant field {field}")
                return False
        return True
