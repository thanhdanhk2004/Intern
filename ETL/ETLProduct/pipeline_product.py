from ETLProduct.transformer import Transformer
from ETLProduct.validator import  Validate
from ETLProduct.mapping_product import Mapping
from ETLCategory.pipeline_category import PipelineCategory
from  ETLProductVariant.pipeline_product_variant import PipelineProductVariant
from ETL.DataExtractLayer.Product import ProductMagento
import yaml
import requests
import time
import json

with open("key.json", "r") as f:
    config = json.load(f)

with open("Mapper/mapping_product.yaml") as f:
    mapper_product = yaml.safe_load(f)

with open("Mapper/mapping_product_medusa.yaml") as f:
    mapper_product_medusa = yaml.safe_load(f)

with open("Mapper/mapping_product_variant.yaml") as f:
    mapper_product_variant = yaml.safe_load(f)

class PipelineProduct:

    array_categories_existed = []

    def __init__(self, products, token_medusa,  token_magento, base_url, retry=30, time_out=3):
        self.products = products
        self.mapper_product = mapper_product
        self.base_url = base_url
        self.retry = retry
        self.time_out = time_out
        self.token_medusa = token_medusa['token']
        self.token_magento = token_magento
        self.array_products = []
        self.mapping = Mapping()
        self.transform = Transformer()
        self.validator = Validate()

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token_medusa}",
            "Content-Type": "application/json"
        })


    def add_product(self, data_product):
        if data_product is None:
            return
        url = f"{self.base_url}/admin/products"

        for i in range(self.retry):
            response = self.session.post(url, json=data_product, timeout=self.time_out)

            if response.status_code == 429:
                print("Please wait")
                time.sleep(1)
                continue

            if response.status_code >= 400:
                raise Exception(f"Error {response.status_code}: {response.text}")

            return response.json()
        raise Exception("Failed")


    # Luong them: Product -> product_variant -> price_set -> product_variant_price_set -> price -> inventory_item -> product_variant_inventory_item -> inventory_level
    # Phải lấy được option ra nữa

    def get_id_options(self, options):
        array_id_options = []
        for option in options:
            array_id_options.append(option["title"])
        return array_id_options

    def add_products(self):
        for product in self.products["items"]:
            if product["type_id"] == "configurable": #CAMTU
                children = ProductMagento(config["magento_url"], self.token_magento).get_children(product["sku"])

                # Fetch simple product and push vào array_products
                for child in children:
                    simple = ProductMagento(config["magento_url"], self.token_magento).get_product_by_sku(child["sku"])
                    mapped = self.mapping.map_field_product(mapper_product, simple, self.token_magento)
                    self.transform.transform_all(mapped)
                    self.array_products.append(mapped)

                # Đặt variant links theo ID hoặc SKU đều ok
                product["extension_attributes"]["configurable_product_links"] = [
                    c["id"] for c in children
                ]

            data = self.mapping.map_field_product(mapper_product, product, self.token_magento)
            self.transform.transform_all(data)
            if self.validator.validate_product(data) == False:
                continue
            elif data['type_id'] == 'simple':
                self.array_products.append(data)
                continue
            elif data['type_id'] == 'configurable':
                data_product_medusa = self.mapping.map_field_product_medusa(data, mapper_product_medusa, self.etl_tag_id)
                product =  self.add_product(data_product_medusa)
                pipeline_category = PipelineCategory(self.token_medusa, self.token_magento, data['categories'])
                pipeline_category.add_category(self.array_categories_existed)
                pipeline_category.add_category_product(product, self.array_categories_existed)
                product_variant_object = PipelineProductVariant(self.base_url, self.token_medusa, self.array_products)

                data_product_variant_medusa = product_variant_object.add_product_variants(data, mapper_product_variant, product["product"]["id"],self.get_id_options(product["product"]["options"]), product)
            else:
                continue
