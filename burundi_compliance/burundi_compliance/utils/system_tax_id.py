from ..api_classes.base import OBRAPIBase

base_data=OBRAPIBase().get_auth_details()

def get_system_tax_id():
    system_tax_id= base_data['system_identification_given_by_obr']
    return system_tax_id
