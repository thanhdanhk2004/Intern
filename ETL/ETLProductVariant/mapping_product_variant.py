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
            title, value = self.get_option_value(product_parent_options, value_variant)
            options[title] = value
        return options

    def get_price_for_product_variant(self, price):
        return {
            "currency_code": "usd",
            "amount": price
        }

    def mapping_variant(self, product_variant, product_parent, option_ids, mapper, product):
        if product_variant is None or product_parent is None:
            return None, None

        # variant = {
        #     "title": "",
        #     "sku":"",
        #     "prices":0,
        #     "options": {}
        # }
        # for field_src, field_target in mapper["fields"].items():
        #     if field_src == "price":
        #         value = [self.get_price_for_product_variant(product_variant["price"])]
        #     elif field_src == "options":
        #         value = self.get_options_value_for_product_variant(product_parent["options"], product_variant["options"], option_ids, product)
        #     else:
        #         value = product_variant[field_src]
        #     variant[field_target] = value
        #
        # return variant
        simple_opts = product_variant["options"]  # CAMTU
        parent_opts = product_parent["options"]
        variant = {
            "title": "",
            "sku": product_variant["sku"],
            "manage_inventory": True,
            "allow_backorder": True,
            "options": {},
            "prices": [
                {"currency_code": "usd", "amount": int(product_variant["price"])}
            ]
        }
        for opt in simple_opts:
            title, value = self.get_option_value(parent_opts, opt)
            if title:
                variant["options"][title] = value

            # auto title: "S / Blue"
        variant["title"] = " / ".join(variant["options"].values())
        internal_thumbnail = None
        if "thumbnail" in product_variant and product_variant["thumbnail"]:
            internal_thumbnail = "http://magento.local/media/catalog/product/" + product_variant["thumbnail"]

        return variant, internal_thumbnail
