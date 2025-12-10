from connectors.magento_connector import MagentoConnector
from connectors.medusa_connector import MedusaConnector
from DataExtractLayer.Customer import CustomerMagento
from DataExtractLayer.Catalog import CatalogMagento
from DataExtractLayer.Order import OrderMagento
from connectors import token_connector
from ETLProduct.pipeline_product import PipelineProduct
from ETLCustomer.pipeline_customer import PipelineCustomer
import requests
import json


with open("key.json", "r") as f:
    config = json.load(f)

quantity_product = 100

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    toke_magento = token_connector.get_token_magento()
    token_medusa = token_connector.get_token_medusa()

    #Phan them san pham
    #connector_magento = MagentoConnector(config["magento_url"], toke_magento)
    # magento_product = connector_magento.get_products(quantity_product,1)
    # pipeline_product = PipelineProduct(magento_product,token_medusa, toke_magento,config["medusa_url"])
    # pipeline_product.add_products()

    #Phan them customer
    pipeline_customer = PipelineCustomer(token_medusa, toke_magento, config["magento_url"], config["medusa_url"])
    pipeline_customer.add_customer_to_medusa()

