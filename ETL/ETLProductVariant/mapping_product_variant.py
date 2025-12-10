

class MappingProductVariant:

    def get_option_value(self, product_parent_options, value_variant):
        for opt in product_parent_options:
            if value_variant["value"] in opt["value_magento"]:
                idx = opt["value_magento"].index(value_variant["value"])
                return opt["title"].lower(), opt["values"][idx]
        return None


    def get_options_value_for_product_variant(self, product_parent_options, values_variant, option_ids, product):
        options = {}
        for value_variant in values_variant:
            title, value =  self.get_option_value(product_parent_options, value_variant)
            options[title] = value
        return options

    def get_price_for_product_variant(self, price):
        return {
            "currency_code":"usd",
            "amount": price
        }

    def mapping_variant(self, product_variant, product_parent, option_ids, mapper, product):

        if product_variant is None or product_parent is None:
            return

        variant = {
            "title": "",
            "sku":"",
            "prices":0,
            "options": {}
        }

        for field_src, field_target in mapper["fields"].items():
            if field_src == "price":
                value = [self.get_price_for_product_variant(product_variant["price"])]
            elif field_src == "options":
                value = self.get_options_value_for_product_variant(product_parent["options"], product_variant["options"], option_ids, product)
            else:
                value = product_variant[field_src]
            variant[field_target] = value

        return variant

