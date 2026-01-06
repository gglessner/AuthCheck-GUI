"""Calypso Technology authentication module."""

module_description = "Calypso (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "Calypso Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "12000"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "environment", "type": "text", "label": "Environment", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Calypso uses proprietary protocol. Web interface on different port."}
]

def authenticate(form_data):
    """Test Calypso authentication."""
    try:
        import socket
        
        host = form_data.get("host", "")
        port = int(form_data.get("port", 12000))
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        sock.close()
        
        return True, f"Calypso port reachable at {host}:{port}"
        
    except Exception as e:
        return False, f"Calypso error: {str(e)}"

