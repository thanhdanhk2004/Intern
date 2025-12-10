from ETLProductVariant.mapping_product_variant import MappingProductVariant
from  ETLProductVariant.validator import ValidateVariant
from ETLProductVariant.transformer import TransformVariant
from DataExtractLayer.ProductVariant import MedusaProductVariant

class PipelineProductVariant:

    def __init__(self, base_url, token, array_products):
        self.array_product = array_products
        self.mapping_product_variant = MappingProductVariant()
        self.validate_variant = ValidateVariant()
        self.transform_variant = TransformVariant()
        self.medusa_product_variant = MedusaProductVariant(base_url, token)


    def get_product_variant_from_array(self, variant_id):
        product_variant_magento = None
        for product in self.array_product:
            if product["id"] == variant_id:
                product_variant_magento = product
                self.array_product.remove(product)
                return product_variant_magento
        return product_variant_magento

    def add_product_variants(self, product_parent, mapper, product_id, option_id, product):
        for variant_id in product_parent["product_variant"]:
            product_variant_magento = self.get_product_variant_from_array(variant_id)
            if product_variant_magento is None:
                continue
            product_variant_medusa = self.mapping_product_variant.mapping_variant(product_variant_magento, product_parent, option_id, mapper, product)
            if self.validate_variant.validate_variant(product_variant_medusa) == False:
                continue
            data = self.medusa_product_variant._request_add_product_variant(product_id, product_variant_medusa)
            print(data)