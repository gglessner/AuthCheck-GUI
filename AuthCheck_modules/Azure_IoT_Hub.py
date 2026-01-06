"""Azure IoT Hub authentication module."""

module_description = "Azure IoT Hub (IoT)"

form_fields = [
    {"name": "connection_string", "type": "password", "label": "IoT Hub Connection String", "default": ""},
    {"name": "hostname", "type": "text", "label": "IoT Hub Hostname", "default": ""},
    {"name": "shared_access_key", "type": "password", "label": "Shared Access Key", "default": ""},
    {"name": "policy_name", "type": "text", "label": "Policy Name", "default": "iothubowner"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Connection string: HostName=xxx.azure-devices.net;SharedAccessKeyName=xxx;SharedAccessKey=xxx"}
]

def authenticate(form_data):
    """Test Azure IoT Hub authentication."""
    try:
        from azure.iot.hub import IoTHubRegistryManager
        
        connection_string = form_data.get("connection_string", "")
        
        if not connection_string:
            hostname = form_data.get("hostname", "")
            policy_name = form_data.get("policy_name", "iothubowner")
            shared_access_key = form_data.get("shared_access_key", "")
            connection_string = f"HostName={hostname};SharedAccessKeyName={policy_name};SharedAccessKey={shared_access_key}"
        
        registry_manager = IoTHubRegistryManager(connection_string)
        
        # Try to query devices
        devices = registry_manager.get_devices(max_number_of_devices=1)
        
        return True, f"Azure IoT Hub authentication successful"
        
    except ImportError:
        return False, "azure-iot-hub library not installed. Install with: pip install azure-iot-hub"
    except Exception as e:
        return False, f"Azure IoT Hub error: {str(e)}"

