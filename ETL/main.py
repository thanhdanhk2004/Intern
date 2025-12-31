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

with open("key.json", "r") as f:
    config = json.load(f)

quantity_product = 2040


def ensure_etl_tag(token_medusa, base_url):
    session = requests.Session()
    session.headers.update({
        "Authorization": f"Bearer {token_medusa['token']}",
        "Content-Type": "application/json"
    })
    get_url = f"{base_url}/admin/product-tags"
    resp = session.get(get_url)
    if resp.status_code != 200:
        raise Exception(f"Không lấy được danh sách tag: {resp.text}")
    tags = resp.json().get("product_tags", [])
    for tag in tags:
        if tag["value"] == "etl_migration":
            return tag["id"]
    create_url = f"{base_url}/admin/product-tags"
    create_resp = session.post(create_url, json={"value": "etl_migration"})
    if create_resp.status_code != 200:
        raise Exception(f"Không tạo được tag: {create_resp.text}")
    tag_id = create_resp.json()["product_tag"]["id"]
    return tag_id


if __name__ == '__main__':
    token_magento = token_connector.get_token_magento()
    token_medusa = token_connector.get_token_medusa()
    etl_tag_id = ensure_etl_tag(token_medusa, config["medusa_url"])

    # THEM PRODUCTS CATEGORIES
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
