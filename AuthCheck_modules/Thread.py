"""Thread/OpenThread authentication module."""

module_description = "Thread/OpenThread (IoT)"

form_fields = [
    {"name": "host", "type": "text", "label": "OTBR Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "REST API Port", "default": "8081"},
    {"name": "network_key", "type": "password", "label": "Network Key (hex)", "default": ""},
    {"name": "extended_pan_id", "type": "text", "label": "Extended PAN ID", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "OpenThread Border Router REST API. Network key is 32 hex chars."}
]

def authenticate(form_data):
    """Test Thread/OpenThread Border Router authentication."""
    try:
        import requests
        
        host = form_data.get("host", "localhost")
        port = form_data.get("port", "8081")
        
        base_url = f"http://{host}:{port}"
        
        # Get node state
        response = requests.get(
            f"{base_url}/node/state",
            timeout=10
        )
        
        if response.status_code == 200:
            state = response.json()
            return True, f"OpenThread Border Router connected (State: {state})"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Thread error: {str(e)}"

