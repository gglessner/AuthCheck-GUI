"""Kronos/UKG Workforce authentication module."""

module_description = "Kronos/UKG (HR)"

form_fields = [
    {"name": "host", "type": "text", "label": "Kronos Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Workforce Central", "Workforce Dimensions", "Pro WFM"], "default": "Workforce Dimensions"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Kronos (now UKG). SuperUser typically for admin."}
]

def authenticate(form_data):
    """Test Kronos authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        product = form_data.get("product", "Workforce Dimensions")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}"
        
        if "Dimensions" in product:
            # OAuth2 for Dimensions
            response = requests.post(
                f"{base_url}/api/authentication/access_token",
                json={"username": username, "password": password},
                verify=verify_ssl,
                timeout=30
            )
        else:
            # Basic auth for WFC
            response = requests.get(
                f"{base_url}/wfc/applications/wtk/html/ess/logon.jsp",
                auth=HTTPBasicAuth(username, password),
                verify=verify_ssl,
                timeout=30
            )
        
        if response.status_code == 200:
            return True, f"Kronos/{product} authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Kronos error: {str(e)}"

