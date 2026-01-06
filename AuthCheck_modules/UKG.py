"""UKG (Ultimate Kronos Group) authentication module."""

module_description = "UKG (HR)"

form_fields = [
    {"name": "host", "type": "text", "label": "API Host", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["UKG Pro", "UKG Dimensions", "UKG Ready"], "default": "UKG Pro"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "UKG (Kronos + Ultimate). API varies by product."}
]

def authenticate(form_data):
    """Test UKG authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        api_key = form_data.get("api_key", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}"
        
        headers = {}
        if api_key:
            headers["Api-Key"] = api_key
        
        response = requests.get(
            f"{base_url}/api/v1/health",
            auth=HTTPBasicAuth(username, password),
            headers=headers,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "UKG authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"UKG error: {str(e)}"

