"""Barracuda authentication module."""

module_description = "Barracuda (Email Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "Appliance Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "api_key", "type": "password", "label": "API Key (Cloud)", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Email Security Gateway", "Web Security Gateway", "CloudGen Firewall", "WAF"], "default": "Email Security Gateway"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: admin. API key from ADVANCED > API."}
]

def authenticate(form_data):
    """Test Barracuda authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "admin")
        password = form_data.get("password", "")
        api_key = form_data.get("api_key", "")
        verify_ssl = form_data.get("verify_ssl", False)
        
        base_url = f"https://{host}:{port}"
        
        if api_key:
            headers = {"Authorization": f"Bearer {api_key}"}
            auth = None
        else:
            headers = {}
            auth = HTTPBasicAuth(username, password)
        
        response = requests.get(
            f"{base_url}/cgi-mod/index.cgi",
            auth=auth,
            headers=headers,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Barracuda authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Barracuda error: {str(e)}"

