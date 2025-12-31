class MappingCustomer:

    def mapping_fields_customer(self, mapper, customer_magento):
        customer_medusa = {}
        for src_field, target_field in mapper['fields'].items():
            value = customer_magento[src_field]
            customer_medusa[target_field] = value

        return customer_medusa

    def mapping_fields_address(self, mapper, address_magento):
        address_medusa = {}
        for src_field, target_field in mapper['fields'].items():
            if src_field == 'street':
                value = address_magento[src_field][0]
            else:
                value = address_magento[src_field]
            address_medusa[target_field] = value

        return address_medusa
