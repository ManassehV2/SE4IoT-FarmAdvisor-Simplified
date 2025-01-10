from .service import AzureTableService

azure_service_instance = AzureTableService()

def get_azure_table_service():
    return azure_service_instance
