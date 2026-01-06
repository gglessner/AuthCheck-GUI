# Azure Event Hubs Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Azure Event Hubs (MQ)"

form_fields = [
    {"name": "connection_string", "type": "password", "label": "Connection String"},
    {"name": "eventhub_name", "type": "text", "label": "Event Hub Name"},
    {"name": "namespace", "type": "text", "label": "Namespace (Alternative)"},
    {"name": "sas_key_name", "type": "text", "label": "SAS Key Name", "default": "RootManageSharedAccessKey"},
    {"name": "sas_key", "type": "password", "label": "SAS Key"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Connection string from Azure Portal > Event Hubs > Shared access policies."},
]


def authenticate(form_data):
    """Attempt to authenticate to Azure Event Hubs."""
    try:
        from azure.eventhub import EventHubConsumerClient
    except ImportError:
        return False, "azure-eventhub package not installed. Run: pip install azure-eventhub"
    
    connection_string = form_data.get('connection_string', '').strip()
    eventhub_name = form_data.get('eventhub_name', '').strip()
    namespace = form_data.get('namespace', '').strip()
    sas_key_name = form_data.get('sas_key_name', '').strip()
    sas_key = form_data.get('sas_key', '').strip()
    
    if not eventhub_name:
        return False, "Event Hub Name is required"
    
    try:
        if connection_string:
            consumer = EventHubConsumerClient.from_connection_string(
                connection_string,
                consumer_group="$Default",
                eventhub_name=eventhub_name
            )
        elif namespace and sas_key_name and sas_key:
            conn_str = f"Endpoint=sb://{namespace}.servicebus.windows.net/;SharedAccessKeyName={sas_key_name};SharedAccessKey={sas_key}"
            consumer = EventHubConsumerClient.from_connection_string(
                conn_str,
                consumer_group="$Default",
                eventhub_name=eventhub_name
            )
        else:
            return False, "Connection String or Namespace with SAS credentials required"
        
        with consumer:
            # Get Event Hub properties
            properties = consumer.get_eventhub_properties()
            partition_count = len(properties.get('partition_ids', []))
            created_at = properties.get('created_at', 'unknown')
            
            # Get partition info
            partition_ids = properties.get('partition_ids', [])
            
            return True, f"Successfully authenticated to Azure Event Hubs\nEvent Hub: {eventhub_name}\nPartitions: {partition_count}\nPartition IDs: {', '.join(partition_ids[:5])}"
        
    except Exception as e:
        error_msg = str(e)
        if 'Unauthorized' in error_msg or '401' in error_msg:
            return False, "Authentication failed: Invalid credentials"
        return False, f"Azure Event Hubs error: {e}"

