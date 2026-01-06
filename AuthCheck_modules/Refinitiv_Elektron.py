"""Refinitiv Elektron Real-Time authentication module."""

module_description = "Refinitiv Elektron (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "ADS/TREP Host", "default": ""},
    {"name": "port", "type": "text", "label": "RSSL Port", "default": "14002"},
    {"name": "username", "type": "text", "label": "DACS Username", "default": ""},
    {"name": "app_id", "type": "text", "label": "Application ID", "default": "256"},
    {"name": "position", "type": "text", "label": "Position", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "RSSL port 14002. DACS for entitlements. Position = IP/hostname."}
]

def authenticate(form_data):
    """Test Refinitiv Elektron connection."""
    try:
        import socket
        
        host = form_data.get("host", "")
        port = int(form_data.get("port", 14002))
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((host, port))
        sock.close()
        
        return True, f"Elektron RSSL port reachable at {host}:{port} (full auth requires RSSL client)"
        
    except Exception as e:
        return False, f"Elektron error: {str(e)}"

