"""PrestaShop authentication module."""

module_description = "PrestaShop (E-commerce)"

form_fields = [
    {"name": "host", "type": "text", "label": "PrestaShop Host", "default": ""},
    {"name": "api_key", "type": "password", "label": "Web Service Key", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "PrestaShop Web Service. Key from Advanced Parameters > Webservice."}
]

def authenticate(form_data):
    """Test PrestaShop authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "").rstrip("/")
        api_key = form_data.get("api_key", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        response = requests.get(
            f"{base_url}/api/",
            auth=HTTPBasicAuth(api_key, ""),
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "PrestaShop authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"PrestaShop error: {str(e)}"

