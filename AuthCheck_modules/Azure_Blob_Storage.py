# Azure Blob Storage Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Azure Blob Storage (Storage)"

form_fields = [
    {"name": "connection_string", "type": "password", "label": "Connection String"},
    {"name": "account_name", "type": "text", "label": "Account Name (Alternative)"},
    {"name": "account_key", "type": "password", "label": "Account Key (Alternative)"},
    {"name": "sas_token", "type": "password", "label": "SAS Token (Alternative)"},
    {"name": "container", "type": "text", "label": "Test Container (Optional)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Connection string from Azure Portal > Storage Account > Access Keys."},
]


def authenticate(form_data):
    """Attempt to authenticate to Azure Blob Storage."""
    try:
        from azure.storage.blob import BlobServiceClient
    except ImportError:
        return False, "azure-storage-blob package not installed. Run: pip install azure-storage-blob"
    
    connection_string = form_data.get('connection_string', '').strip()
    account_name = form_data.get('account_name', '').strip()
    account_key = form_data.get('account_key', '').strip()
    sas_token = form_data.get('sas_token', '').strip()
    container = form_data.get('container', '').strip()
    
    try:
        if connection_string:
            client = BlobServiceClient.from_connection_string(connection_string)
        elif account_name and account_key:
            account_url = f"https://{account_name}.blob.core.windows.net"
            client = BlobServiceClient(account_url=account_url, credential=account_key)
        elif account_name and sas_token:
            account_url = f"https://{account_name}.blob.core.windows.net"
            client = BlobServiceClient(account_url=account_url, credential=sas_token)
        else:
            return False, "Connection String or Account Name with Key/SAS required"
        
        if container:
            # Test specific container
            container_client = client.get_container_client(container)
            props = container_client.get_container_properties()
            return True, f"Successfully authenticated to Azure Blob Storage\nContainer: {container}\nLast Modified: {props.get('last_modified', 'unknown')}"
        else:
            # List containers
            containers = list(client.list_containers())
            container_names = [c['name'] for c in containers[:5]]
            
            # Get account info
            account_info = client.get_account_information()
            sku = account_info.get('sku_name', 'unknown')
            
            return True, f"Successfully authenticated to Azure Blob Storage\nSKU: {sku}\nContainers: {len(containers)}\nSample: {', '.join(container_names) if container_names else 'none'}"
        
    except Exception as e:
        error_msg = str(e)
        if 'AuthenticationFailed' in error_msg:
            return False, "Authentication failed: Invalid credentials"
        return False, f"Azure Blob Storage error: {e}"

