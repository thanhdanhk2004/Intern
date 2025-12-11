
class TransformVariant:

    url_image = "http://magento.local/media/catalog/product/"

    def transform_image(self, product_variant):
        if product_variant.get("thumbnail"):
            product_variant["thumbnail"] = self.url_image + product_variant["thumbnail"]

    def transform_variant_all(self, product_variant):
        self.transform_image(product_variant)