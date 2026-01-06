"""Trend Micro authentication module."""

module_description = "Trend Micro (EDR)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "username", "type": "text", "label": "Username (Alt)", "default": ""},
    {"name": "password", "type": "password", "label": "Password (Alt)", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Vision One", "Apex One", "Deep Security", "Cloud One"], "default": "Vision One"},
    {"name": "region", "type": "combo", "label": "Region", "options": ["us", "eu", "au", "jp", "sg", "in"], "default": "us"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Trend Micro. API key from Administration > API Keys."}
]

def authenticate(form_data):
    """Test Trend Micro authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        api_key = form_data.get("api_key", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        product = form_data.get("product", "Vision One")
        region = form_data.get("region", "us")
        
        if product == "Vision One":
            base_url = f"https://api.xdr.trendmicro.com"
            response = requests.get(
                f"{base_url}/v3.0/healthcheck/connectivity",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30
            )
        elif product == "Deep Security":
            base_url = f"https://{host}:{port}/api"
            response = requests.get(
                f"{base_url}/apiusage",
                headers={"api-secret-key": api_key},
                timeout=30,
                verify=False
            )
        else:
            base_url = f"https://{host}:{port}"
            response = requests.get(
                f"{base_url}/api/v1/status",
                auth=HTTPBasicAuth(username, password) if username else None,
                headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
                timeout=30,
                verify=False
            )
        
        if response.status_code == 200:
            return True, f"Trend Micro {product} authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Trend Micro error: {str(e)}"

