import re

class Transformer:
    url_image = "https://localhost/pub/media/catalog/product/"

    def clean_html(self, product):
        if product.get("description"):
            product["description"] = re.sub(r"<.*?>", "", product["description"])

    def transform_price(self, product):
        if product.get("amount"):
            product["amount"] = int(product.get("amount"))

    def transform_image(self, product):
        if product.get("thumbnail"):
            product["thumbnail"] = self.url_image + product["thumbnail"]

    def transform_all(self, product):
        self.transform_price(product)
        self.transform_image(product)
        self.clean_html(product)

