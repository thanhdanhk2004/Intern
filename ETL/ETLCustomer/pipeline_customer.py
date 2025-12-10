# luồng thêm customer: group -> customers (tất cả đều qua phân trang)
import yaml
from ETLCustomer.validator import ValidateCustomer
from ETLCustomer.mapping_customer import MappingCustomer
from DataExtractLayer.Group import GroupMagento
from MedusaDataExtractLayer.Group import GroupMedusa
from DataExtractLayer.Customer import CustomerMagento
from MedusaDataExtractLayer.Customer import CustomerMedusa
from MedusaDataExtractLayer.CustomerGroup import CustomerGroupMedusa
from MedusaDataExtractLayer.Address import CustomerAddressMedusa
from MedusaDataExtractLayer.User import UserMedusa

with open("Mapper/mapping_customer.yaml") as f:
    mapper_customer = yaml.safe_load(f)

with open("Mapper/mapping_address.yaml") as f:
    mapper_address = yaml.safe_load(f)

class PipelineCustomer:
    array_groups_existed = []
    page_size = -1
    page_current = -1

    def __init__(self, token_medusa, token_magento, url_magento, url_medusa):
        self.token_medusa = token_medusa['token']
        self.token_magento = token_magento
        self.array_groups_existed = []
        self.url_magento = url_magento
        self.url_medusa = url_medusa
        self.mapping_customer = MappingCustomer()
        self.validate_customer = ValidateCustomer()
        self.group_medusa = GroupMedusa(url_medusa, token_medusa['token'])
        self.customer_medusa = CustomerMedusa(url_medusa, token_medusa['token'])
        self.customer_group_medusa = CustomerGroupMedusa(url_medusa, token_medusa['token'])
        self.customer_address_medusa = CustomerAddressMedusa(url_medusa, token_medusa['token'])
        self.page_size = 10
        self.page_current = 1

    def add_group_to_medusa(self):
        group_magento = GroupMagento(self.url_magento, self.token_magento)
        groups = group_magento.load_group(self.page_size, self.page_current)
        if groups:
            for group in groups['items']:
                response = self.group_medusa._request_add_group(group["code"])
                if response:
                    self.array_groups_existed.append({group["id"]: response["customer_group"]["id"]})

    def groups_id_medusa(self, group_id_magento):
        for group in self.array_groups_existed:
            if group_id_magento in group:
                return group[group_id_magento]
        return None


    def add_customer_to_medusa(self):
        self.add_group_to_medusa()

        customer_magento = CustomerMagento(self.url_magento, self.token_magento)
        customers = customer_magento.load_customer(self.page_size, self.page_current)

        if customers:

            for customer in customers["items"]:
                customer_medusa_mapping = self.mapping_customer.mapping_fields_customer(mapper_customer, customer)
                if customer_medusa_mapping:
                    if self.validate_customer.validate_field_customer(customer_medusa_mapping) == False:
                        continue
                    response_add_customer = self.customer_medusa._request_add_customer(customer_medusa_mapping)
                    if response_add_customer is None:
                        continue

                    group_id = self.groups_id_medusa(customer["group_id"])
                    if group_id is None:
                        continue
                    response_add_customer_group = self.customer_group_medusa._request_add_customer_group(group_id, response_add_customer["customer"]["id"])

                    for address in customer["addresses"]:
                        customer_address_mapping = self.mapping_customer.mapping_fields_address(mapper_address, address)
                        if customer_address_mapping:
                            response_add_customer_address = self.customer_address_medusa._request_add_customer_address(response_add_customer["customer"]["id"], customer_address_mapping)

                    user_medusa = UserMedusa(self.url_medusa, self.token_medusa)
                    response_add_user = user_medusa._request_add_user(customer_medusa_mapping["email"])
                    if response_add_user:
                        response_reset_password = user_medusa._request_reset_password(customer_medusa_mapping["email"])







