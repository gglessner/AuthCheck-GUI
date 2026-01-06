"""Infor authentication module."""

module_description = "Infor (ERP)"

form_fields = [
    {"name": "host", "type": "text", "label": "Infor Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["CloudSuite", "LN", "M3", "Lawson", "SunSystems"], "default": "CloudSuite"},
    {"name": "tenant", "type": "text", "label": "Tenant", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Infor ERP products. CloudSuite uses Infor OS authentication."}
]

def authenticate(form_data):
    """Test Infor authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        tenant = form_data.get("tenant", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}"
        
        headers = {}
        if tenant:
            headers["X-Infor-Tenant"] = tenant
        
        response = requests.get(
            f"{base_url}/api/v1/health",
            auth=HTTPBasicAuth(username, password),
            headers=headers,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Infor authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Infor error: {str(e)}"

