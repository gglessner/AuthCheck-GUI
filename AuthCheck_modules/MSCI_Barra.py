"""MSCI Barra authentication module."""

module_description = "MSCI Barra (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "api.msci.com"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Barra Portfolio Manager", "RiskMetrics", "BarraOne"], "default": "BarraOne"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "MSCI Barra risk models. BarraOne cloud, RiskMetrics."}
]

def authenticate(form_data):
    """Test MSCI Barra authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "api.msci.com")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        api_key = form_data.get("api_key", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}"
        
        headers = {}
        if api_key:
            headers["x-api-key"] = api_key
        
        auth = HTTPBasicAuth(username, password) if username else None
        
        response = requests.get(
            f"{base_url}/api/v1/health",
            auth=auth,
            headers=headers,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "MSCI Barra authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"MSCI Barra error: {str(e)}"

