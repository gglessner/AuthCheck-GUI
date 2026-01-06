"""Ellucian Banner authentication module."""

module_description = "Ellucian Banner (LMS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Banner Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "api_key", "type": "password", "label": "API Key (Ethos)", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Banner 9", "Ethos Integration", "Banner INB"], "default": "Banner 9"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Ellucian Banner. Common: BASELINE / password. Ethos for API."}
]

def authenticate(form_data):
    """Test Ellucian Banner authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        api_key = form_data.get("api_key", "")
        product = form_data.get("product", "Banner 9")
        verify_ssl = form_data.get("verify_ssl", True)
        
        if product == "Ethos Integration" and api_key:
            response = requests.get(
                "https://integrate.elluciancloud.com/auth",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30
            )
        else:
            base_url = f"https://{host}:{port}"
            response = requests.get(
                f"{base_url}/StudentSelfService/ssb/",
                auth=HTTPBasicAuth(username, password),
                verify=verify_ssl,
                timeout=30
            )
        
        if response.status_code == 200:
            return True, f"Ellucian Banner {product} authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Banner error: {str(e)}"

