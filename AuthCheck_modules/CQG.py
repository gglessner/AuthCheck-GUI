"""CQG authentication module."""

module_description = "CQG (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "CQG Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["CQG Integrated Client", "CQG QTrader", "CQG Desktop", "CQG API"], "default": "CQG API"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "CQG trading platform. WebAPI available. FIX connectivity."}
]

def authenticate(form_data):
    """Test CQG authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        
        base_url = f"https://{host}:{port}"
        
        response = requests.get(
            f"{base_url}/api/v1/health",
            auth=HTTPBasicAuth(username, password),
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "CQG authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"CQG error: {str(e)}"

