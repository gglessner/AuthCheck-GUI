"""TSYS (Global Payments) authentication module."""

module_description = "TSYS (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "TSYS Host", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "merchant_id", "type": "text", "label": "Merchant ID", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["TS2", "PRIME", "Genius"], "default": "TS2"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TSYS (Global Payments). TS2 for issuer processing."}
]

def authenticate(form_data):
    """Test TSYS authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "").rstrip("/")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        product = form_data.get("product", "TS2")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        response = requests.get(
            f"{base_url}/api/v1/health",
            auth=HTTPBasicAuth(username, password),
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"TSYS {product} authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"TSYS error: {str(e)}"

