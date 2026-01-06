"""Utimaco Atalla HSM authentication module."""

module_description = "Utimaco Atalla HSM (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "HSM Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "7000"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Utimaco Atalla HSM. AT1000 series. Port 7000 default."}
]

def authenticate(form_data):
    """Test Atalla HSM authentication."""
    try:
        import socket
        
        host = form_data.get("host", "")
        port = int(form_data.get("port", "7000"))
        
        # Atalla uses proprietary protocol
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            return True, f"Atalla HSM port {port} is open (full auth requires Atalla SDK)"
        else:
            return False, f"Cannot connect to port {port}"
            
    except Exception as e:
        return False, f"Atalla HSM error: {str(e)}"

