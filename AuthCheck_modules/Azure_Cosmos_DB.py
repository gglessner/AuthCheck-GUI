# Azure Cosmos DB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Azure Cosmos DB (DB)"

form_fields = [
    {"name": "endpoint", "type": "text", "label": "Account Endpoint"},
    {"name": "key", "type": "password", "label": "Account Key"},
    {"name": "connection_string", "type": "password", "label": "Connection String (Alternative)"},
    {"name": "database", "type": "text", "label": "Test Database (Optional)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Endpoint: https://accountname.documents.azure.com:443/. Keys from Azure Portal > Keys."},
]


def authenticate(form_data):
    """Attempt to authenticate to Azure Cosmos DB."""
    try:
        from azure.cosmos import CosmosClient
    except ImportError:
        return False, "azure-cosmos package not installed. Run: pip install azure-cosmos"
    
    endpoint = form_data.get('endpoint', '').strip()
    key = form_data.get('key', '').strip()
    connection_string = form_data.get('connection_string', '').strip()
    database = form_data.get('database', '').strip()
    
    try:
        if connection_string:
            client = CosmosClient.from_connection_string(connection_string)
        elif endpoint and key:
            client = CosmosClient(endpoint, credential=key)
        else:
            return False, "Endpoint with Key or Connection String required"
        
        # List databases
        databases = list(client.list_databases())
        db_names = [db['id'] for db in databases[:5]]
        
        if database:
            # Get specific database info
            db_client = client.get_database_client(database)
            containers = list(db_client.list_containers())
            return True, f"Successfully authenticated to Cosmos DB\nDatabase: {database}\nContainers: {len(containers)}"
        
        return True, f"Successfully authenticated to Azure Cosmos DB\nDatabases: {len(databases)}\nSample: {', '.join(db_names) if db_names else 'none'}"
        
    except Exception as e:
        error_msg = str(e)
        if 'Unauthorized' in error_msg or '401' in error_msg:
            return False, "Authentication failed: Invalid credentials"
        return False, f"Cosmos DB error: {e}"

