import json
from DataExtractLayer.Option import OptionMagento
from DataExtractLayer.Product import ProductMagento

with open("key.json", "r") as f:
    config = json.load(f)


class Mapping:
    def get_lable_option(self, options):
        label_options = []
        value_options = []
        for option in options:
            label_options.append(option["label"])
            value_options.append(option["value"])
        return label_options, value_options

    def get_value_variant_for_simple(self, product):
        arr_value_variant_for_simple = []
        for custom_attribute in product["custom_attributes"]:
            if custom_attribute["attribute_code"].lower() == "size" or custom_attribute[
                "attribute_code"].lower() == "color":
                arr_value_variant_for_simple.append({
                    "title": custom_attribute["attribute_code"].lower(),
                    # "value":custom_attribute["value"]})
                    "value": str(custom_attribute["value"])})  # CAMTU
        return arr_value_variant_for_simple

    def map_field_option(self, product, mapper, token):
        option_magento = OptionMagento(config["magento_url"], token)
        data_options_medusa = []
        for option in product["extension_attributes"]["configurable_product_options"]:
            data_option = option_magento.get_option(option["attribute_id"])
            if data_option is None:
                continue
            # option_medusa = {}
            # option_medusa["title"] = data_option["attribute_code"].lower()
            # option_medusa["values"], option_medusa["value_magento"] = self.get_lable_option(data_option["options"])
            usable_values = option["values"]  # CAMTU
            filtered_labels = []
            filtered_values = []
            for value in usable_values:
                for option in data_option["options"]:
                    if option["value"] == str(value["value_index"]):
                        filtered_labels.append(option["label"])
                        filtered_values.append(option["value"])
            option_medusa = {
                "title": data_option["attribute_code"].lower(),
                "values": filtered_labels,
                "value_magento": filtered_values
            }
            data_options_medusa.append(option_medusa)
        return data_options_medusa

    def map_field_quantity(self, sku, token, field):
        product_magento = ProductMagento(config["magento_url"], token)
        data_product = product_magento.get_product_by_sku(sku)
        return data_product["extension_attributes"]["stock_item"][field]

    def map_field_product(self, mapper, product, token):
        target_data = {}
        value = None
        custom_attr = {attr["attribute_code"]: attr["value"] for attr in product["custom_attributes"]}
        for src_field, target_field in mapper['fields'].items():
            if src_field == 'description':
                value = custom_attr.get('description', '')
            elif src_field == "categories":
                value = product['extension_attributes'][target_field]
            elif src_field == 'thumbnail':
                value = product['media_gallery_entries'][0][target_field]
            elif src_field == "product_variant" and product['type_id'] == 'configurable':
                value = product['extension_attributes'][target_field]
            elif src_field == "options" and product["type_id"] == 'configurable':
                value = self.map_field_option(product, mapper, token)
            elif src_field == "quantity":
                value = 10000  # self.map_field_quantity(product["sku"], token, target_field)
            else:
                if src_field == 'product_variant':
                    continue
                if src_field == 'options' and product['type_id'] == 'simple':
                    value = self.get_value_variant_for_simple(product)
                else:
                    if target_field not in product:
                        continue
                    value = product[target_field]
            target_data[src_field] = value
        return target_data

    def map_field_product_medusa(self, data, mapper, tag_id):
        target_data = {}
        for src_field, target_field in mapper['fields'].items():
            value = data[target_field]
            target_data[src_field] = value
        if target_data["status"] == 1:
            target_data["status"] = "published"
        else:
            target_data["status"] = "draft"
        target_data["tags"] = [{"id": tag_id}]
        return target_data
