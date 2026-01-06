"""Blue Yonder (JDA) authentication module."""

module_description = "Blue Yonder (Supply Chain)"

form_fields = [
    {"name": "host", "type": "text", "label": "Blue Yonder Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "tenant", "type": "text", "label": "Tenant", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Luminate", "WMS", "Workforce"], "default": "Luminate"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Blue Yonder (formerly JDA). Supply chain and fulfillment."}
]

def authenticate(form_data):
    """Test Blue Yonder authentication."""
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
            headers["X-Tenant-ID"] = tenant
        
        response = requests.get(
            f"{base_url}/api/v1/health",
            auth=HTTPBasicAuth(username, password),
            headers=headers,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Blue Yonder authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Blue Yonder error: {str(e)}"

