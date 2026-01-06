"""PAX payment terminal authentication module."""

module_description = "PAX (ATM)"

form_fields = [
    {"name": "host", "type": "text", "label": "Terminal Host/IP", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "10009"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["A-Series", "E-Series", "S-Series", "Aries"], "default": "A-Series"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "PAX Technology. BroadPOS. Default admin password varies."}
]

def authenticate(form_data):
    """Test PAX authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "10009")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", False)
        
        # PAX uses HTTP on port 10009 typically
        protocol = "https" if verify_ssl else "http"
        base_url = f"{protocol}://{host}:{port}"
        
        response = requests.get(
            f"{base_url}/api/status",
            auth=HTTPBasicAuth(username, password),
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "PAX terminal authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"PAX error: {str(e)}"

