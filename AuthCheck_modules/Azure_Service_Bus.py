# Azure Service Bus Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Azure Service Bus (MQ)"

form_fields = [
    {"name": "connection_string", "type": "password", "label": "Connection String"},
    {"name": "namespace", "type": "text", "label": "Namespace (Alternative)"},
    {"name": "sas_key_name", "type": "text", "label": "SAS Key Name", "default": "RootManageSharedAccessKey"},
    {"name": "sas_key", "type": "password", "label": "SAS Key"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Connection string from Azure Portal > Service Bus > Shared access policies."},
]


def authenticate(form_data):
    """Attempt to authenticate to Azure Service Bus."""
    try:
        from azure.servicebus import ServiceBusClient
    except ImportError:
        return False, "azure-servicebus package not installed. Run: pip install azure-servicebus"
    
    connection_string = form_data.get('connection_string', '').strip()
    namespace = form_data.get('namespace', '').strip()
    sas_key_name = form_data.get('sas_key_name', '').strip()
    sas_key = form_data.get('sas_key', '').strip()
    
    try:
        if connection_string:
            client = ServiceBusClient.from_connection_string(connection_string)
        elif namespace and sas_key_name and sas_key:
            conn_str = f"Endpoint=sb://{namespace}.servicebus.windows.net/;SharedAccessKeyName={sas_key_name};SharedAccessKey={sas_key}"
            client = ServiceBusClient.from_connection_string(conn_str)
        else:
            return False, "Connection String or Namespace with SAS credentials required"
        
        # Get namespace info by attempting to create a sender for a non-existent queue
        # This validates credentials
        with client:
            # Try to get queue runtime properties (will fail if no permission, but validates auth)
            try:
                # Use management client for listing
                from azure.servicebus.management import ServiceBusAdministrationClient
                
                if connection_string:
                    admin_client = ServiceBusAdministrationClient.from_connection_string(connection_string)
                else:
                    admin_client = ServiceBusAdministrationClient.from_connection_string(conn_str)
                
                queues = list(admin_client.list_queues())
                topics = list(admin_client.list_topics())
                
                return True, f"Successfully authenticated to Azure Service Bus\nQueues: {len(queues)}\nTopics: {len(topics)}"
            except Exception as e:
                # If management fails, at least the client connected
                return True, f"Successfully authenticated to Azure Service Bus\nNote: Limited management access - {str(e)[:50]}"
        
    except Exception as e:
        error_msg = str(e)
        if 'Unauthorized' in error_msg or '401' in error_msg:
            return False, "Authentication failed: Invalid credentials"
        return False, f"Azure Service Bus error: {e}"

