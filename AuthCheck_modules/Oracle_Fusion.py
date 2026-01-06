"""Oracle Fusion Cloud authentication module."""

module_description = "Oracle Fusion Cloud (ERP)"

form_fields = [
    {"name": "host", "type": "text", "label": "Fusion Host", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["ERP", "HCM", "SCM", "CX"], "default": "ERP"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Oracle Fusion Cloud Applications. REST API on /fscmRestApi/."}
]

def authenticate(form_data):
    """Test Oracle Fusion Cloud authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}"
        
        response = requests.get(
            f"{base_url}/fscmRestApi/resources/latest",
            auth=HTTPBasicAuth(username, password),
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Oracle Fusion Cloud authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Oracle Fusion error: {str(e)}"

