"""SS&C Advent investment management authentication module."""

module_description = "SS&C Advent (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "Advent Host", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Geneva", "APX", "Moxy", "Axys"], "default": "Geneva"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "SS&C Advent. Geneva, APX for portfolio management."}
]

def authenticate(form_data):
    """Test SS&C Advent authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "").rstrip("/")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        product = form_data.get("product", "Geneva")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        response = requests.get(
            f"{base_url}/api/v1/status",
            auth=HTTPBasicAuth(username, password),
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"SS&C Advent {product} authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"SS&C Advent error: {str(e)}"

