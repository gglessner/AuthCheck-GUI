"""Nutanix Prism authentication module."""

module_description = "Nutanix Prism (Virtualization)"

form_fields = [
    {"name": "host", "type": "text", "label": "Prism Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "9440",
     "port_toggle": "verify_ssl", "tls_port": "9440", "non_tls_port": "9440"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 9440 (TLS default). admin / admin (first login)."}
]

def authenticate(form_data):
    """Test Nutanix Prism authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "localhost")
        port = form_data.get("port", "9440")
        username = form_data.get("username", "admin")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", False)
        
        base_url = f"https://{host}:{port}/api/nutanix/v3"
        
        response = requests.get(
            f"{base_url}/users/me",
            auth=HTTPBasicAuth(username, password),
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"Nutanix Prism authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Nutanix error: {str(e)}"

