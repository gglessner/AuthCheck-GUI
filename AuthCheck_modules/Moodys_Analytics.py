"""Moody's Analytics authentication module."""

module_description = "Moody's Analytics (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "Moody's Host", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["RiskCalc", "CreditEdge", "RiskAuthority"], "default": "RiskCalc"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Moody's Analytics. Credit risk and analytics."}
]

def authenticate(form_data):
    """Test Moody's Analytics authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "").rstrip("/")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        api_key = form_data.get("api_key", "")
        product = form_data.get("product", "RiskCalc")
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
        
        response = requests.get(
            f"{base_url}/api/v1/status",
            auth=HTTPBasicAuth(username, password) if username else None,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"Moody's Analytics {product} authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Moody's Analytics error: {str(e)}"

