"""OPC UA authentication module."""

module_description = "OPC UA (ICS)"

form_fields = [
    {"name": "endpoint", "type": "text", "label": "Endpoint URL", "default": "opc.tcp://localhost:4840"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "security_mode", "type": "combo", "label": "Security Mode", "options": ["None", "Sign", "SignAndEncrypt"], "default": "None"},
    {"name": "security_policy", "type": "combo", "label": "Security Policy", "options": ["None", "Basic128Rsa15", "Basic256", "Basic256Sha256"], "default": "None"},
    {"name": "certificate", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.der *.crt)"},
    {"name": "private_key", "type": "file", "label": "Private Key", "filter": "Key Files (*.pem *.key)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: anonymous access. Common users: admin/admin, user/password"}
]

def authenticate(form_data):
    """Test OPC UA authentication."""
    try:
        from opcua import Client
        
        endpoint = form_data.get("endpoint", "opc.tcp://localhost:4840")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        
        client = Client(endpoint)
        
        if username and password:
            client.set_user(username)
            client.set_password(password)
        
        client.connect()
        
        # Try to browse root
        root = client.get_root_node()
        children = root.get_children()
        
        client.disconnect()
        return True, f"OPC UA authentication successful to {endpoint}"
        
    except ImportError:
        return False, "opcua library not installed. Install with: pip install opcua"
    except Exception as e:
        return False, f"OPC UA error: {str(e)}"

