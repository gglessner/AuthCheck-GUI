"""Diebold Nixdorf ATM authentication module."""

module_description = "Diebold Nixdorf ATM (ATM)"

form_fields = [
    {"name": "host", "type": "text", "label": "ATM Host/IP", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "interface", "type": "combo", "label": "Interface", "options": ["Web Management", "DDC Protocol", "Agilis"], "default": "Web Management"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Diebold Nixdorf. Agilis platform. Common: admin / password. DDC port 5001."}
]

def authenticate(form_data):
    """Test Diebold Nixdorf ATM authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        interface = form_data.get("interface", "Web Management")
        verify_ssl = form_data.get("verify_ssl", False)
        
        if interface == "DDC Protocol":
            # DDC is proprietary - basic TCP check
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host, int(port)))
            sock.close()
            if result == 0:
                return True, f"Diebold DDC port {port} is open (protocol auth requires specialized client)"
            else:
                return False, f"Cannot connect to DDC port {port}"
        else:
            base_url = f"https://{host}:{port}"
            
            response = requests.get(
                f"{base_url}/api/v1/status",
                auth=HTTPBasicAuth(username, password),
                verify=verify_ssl,
                timeout=30
            )
        
        if response.status_code == 200:
            return True, "Diebold Nixdorf ATM authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Diebold Nixdorf error: {str(e)}"

