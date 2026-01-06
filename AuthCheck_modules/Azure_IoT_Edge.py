"""Azure IoT Edge authentication module."""

module_description = "Azure IoT Edge (IoT)"

form_fields = [
    {"name": "connection_string", "type": "password", "label": "IoT Hub Connection String", "default": ""},
    {"name": "device_id", "type": "text", "label": "Edge Device ID", "default": ""},
    {"name": "module_id", "type": "text", "label": "Module ID", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Edge devices registered in IoT Hub. Connection string from Azure Portal."}
]

def authenticate(form_data):
    """Test Azure IoT Edge authentication."""
    try:
        from azure.iot.hub import IoTHubRegistryManager
        
        connection_string = form_data.get("connection_string", "")
        device_id = form_data.get("device_id", "")
        
        registry_manager = IoTHubRegistryManager(connection_string)
        
        if device_id:
            device = registry_manager.get_device(device_id)
            if device.capabilities.iot_edge:
                return True, f"Azure IoT Edge device found: {device_id}"
            else:
                return False, f"Device {device_id} is not an Edge device"
        else:
            # List edge devices
            devices = registry_manager.get_devices(max_number_of_devices=100)
            edge_devices = [d for d in devices if d.capabilities.iot_edge]
            return True, f"Azure IoT Edge auth successful ({len(edge_devices)} edge devices)"
            
    except ImportError:
        return False, "azure-iot-hub library not installed. Install with: pip install azure-iot-hub"
    except Exception as e:
        return False, f"Azure IoT Edge error: {str(e)}"

