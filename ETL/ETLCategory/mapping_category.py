
class MappingCategory:

    def get_handle(self, custom_attributes):
        for custom_attribute in custom_attributes:
            if custom_attribute["attribute_code"] == "url_key":
                return custom_attribute["value"]
        return "not handle"

    def map_field_category(self, category_data, mapper):
        target_data = {}
        for target_filed, src_field in mapper['fields'].items():
            if target_filed == "handle":
                value = self.get_handle(category_data["custom_attributes"])
            else:
                value = category_data[src_field]
            target_data[target_filed] = value
        return target_data

    