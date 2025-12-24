from ETL.ETLOrder.pipeline_order import PipelineOrder
from connectors.magento_connector import MagentoConnector
from connectors.medusa_connector import MedusaConnector
from DataExtractLayer.Customer import CustomerMagento
from DataExtractLayer.Catalog import CatalogMagento
from DataExtractLayer.Order import OrderMagento
from connectors import token_connector
from ETLProduct.pipeline_product import PipelineProduct
from ETLCustomer.pipeline_customer import PipelineCustomer
from ETLCleaner.clear_products import CleanupProducts
from ETLCleaner.clear_categories import CleanupCategories
from ETLCleaner.clean_customers import CleanupCustomerData
import requests
import json
from ETLProduct.insert_tag import ensure_etl_tag

with open("key.json", "r") as f:
    config = json.load(f)

quantity_product = 2040

if __name__ == '__main__':
    token_magento = token_connector.get_token_magento()
    token_medusa = token_connector.get_token_medusa()

    # THEM PRODUCTS CATEGORIES
    etl_tag_id = ensure_etl_tag(token_medusa, config["medusa_url"])
    # connector_magento = MagentoConnector(config["magento_url"], token_magento)
    # magento_product = connector_magento.get_products(quantity_product, 1)
    # pipeline_product = PipelineProduct(magento_product, token_medusa, token_magento, config["medusa_url"])
    # pipeline_product.etl_tag_id = etl_tag_id
    # pipeline_product.add_products()

    # XOA PRODUCTS CATEGORIES
    # cleanupProducts = CleanupProducts(token_medusa, config["medusa_url"])
    # cleanupProducts.clear_products()
    # cleanupCategories = CleanupCategories(token_medusa, config["medusa_url"])
    # cleanupCategories.clear_categories()

    # THEM CUSTOMERS
    # pipeline_customer = PipelineCustomer(token_medusa, token_magento, config["magento_url"], config["medusa_url"])
    # pipeline_customer.add_customer_to_medusa()

    # XOA CUSTOMERS
    # cleanupCustomers = CleanupCustomerData(config["medusa_url"], token_medusa)
    # cleanupCustomers.clear_all()

    pipeline_order = PipelineOrder(
        token_medusa=token_medusa["token"],
        token_magento=token_magento,
        magento_base_url=config["magento_url"],
        medusa_base_url=config["medusa_url"],
    )

    pipeline_order.run(page_size=50, page=1)
