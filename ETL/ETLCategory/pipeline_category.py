import json
import  yaml
from  ETLCategory.mapping_category import  MappingCategory
from ETLCategory.validator import ValidatorCategory
from DataExtractLayer.Categories import CategoriesMagento
from MedusaDataExtractLayer.Categories import MedusaCategory
from  DataExtractLayer.ProductCategory import MedusaProductCategory

with open("key.json", "r") as f:
    config = json.load(f)

with open("Mapper/mapping_category.yaml" ) as f:
    mapper = yaml.safe_load(f)


class PipelineCategory:

    def __init__(self, token_medusa, token_magento, categories):
        self.token_medusa = token_medusa
        self.token_magento = token_magento
        self.categories = categories
        self.magento_categories = CategoriesMagento(config["magento_url"], token_magento)
        self.mapping_category = MappingCategory()
        self.validate_category = ValidatorCategory()
        self.medusa_category = MedusaCategory(config["medusa_url"], token_medusa)
        self.medusa_product_category = MedusaProductCategory(config["medusa_url"], token_medusa)

    def check_category_in_array(self, category_id, array_existed_categories):
        for item in array_existed_categories:
            if item["category_id_magento"] == category_id:
                return True
        return False

    def add_category(self, array_existed_categories):
        for category in self.categories:
            if self.check_category_in_array(category['category_id'], array_existed_categories):
                continue

            data_category_magento = self.magento_categories.load_catalog(category['category_id'])
            if data_category_magento is None:
                continue

            data_category_medusa = self.mapping_category.map_field_category(data_category_magento, mapper)
            if data_category_medusa is None:
                continue

            if self.validate_category.validate_categories(data_category_medusa) == False:
                continue

            data_category_medusa_return = self.medusa_category._request_add_category(data_category_medusa)
            if data_category_medusa_return:
                array_existed_categories.append({
                    "category_id_magento": category['category_id'],
                    "category_id_medusa": data_category_medusa_return['product_category']['id']
                })

    def get_category_id_in_array(self, array_existed_categories, category_id_in_magento):
        for item in array_existed_categories:
            if item["category_id_magento"] == category_id_in_magento:
                return item["category_id_medusa"]
        return -1

    def add_category_product(self, product,array_existed_categories):
        for category in self.categories:
            category_id_in_medusa = self.get_category_id_in_array(array_existed_categories, category["category_id"])
            if category_id_in_medusa == -1:
                continue
            self.medusa_product_category._request_add_product_category(category_id_in_medusa, product)