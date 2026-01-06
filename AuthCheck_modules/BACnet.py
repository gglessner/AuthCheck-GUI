"""BACnet authentication module."""

module_description = "BACnet (ICS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "47808"},
    {"name": "device_id", "type": "text", "label": "Device ID", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "BACnet/IP port 47808. No authentication in standard BACnet."}
]

def authenticate(form_data):
    """Test BACnet connection."""
    try:
        import BAC0
        
        host = form_data.get("host", "localhost")
        port = int(form_data.get("port", 47808))
        
        # Initialize BACnet network
        bacnet = BAC0.lite()
        
        # Try to discover devices
        bacnet.discover()
        
        bacnet.disconnect()
        return True, f"BACnet network initialized successfully"
        
    except ImportError:
        return False, "BAC0 library not installed. Install with: pip install BAC0"
    except Exception as e:
        return False, f"BACnet error: {str(e)}"

