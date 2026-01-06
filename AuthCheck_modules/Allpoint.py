"""Allpoint ATM Network authentication module."""

module_description = "Allpoint (ATM)"

form_fields = [
    {"name": "host", "type": "text", "label": "Allpoint Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Allpoint (Cardtronics). Surcharge-free ATM network."}
]

def authenticate(form_data):
    """Test Allpoint authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        api_key = form_data.get("api_key", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}"
        
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
        
        response = requests.get(
            f"{base_url}/api/v1/locations",
            auth=HTTPBasicAuth(username, password) if username else None,
            headers=headers,
            params={"limit": 1},
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Allpoint authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Allpoint error: {str(e)}"

