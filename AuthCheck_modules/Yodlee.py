"""Yodlee Envestnet authentication module."""

module_description = "Yodlee (Payment)"

form_fields = [
    {"name": "host", "type": "text", "label": "API Host", "default": "sandbox.api.yodlee.com"},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "api_version", "type": "text", "label": "API Version", "default": "1.1"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Yodlee (Envestnet). Sandbox vs production host differs."}
]

def authenticate(form_data):
    """Test Yodlee authentication."""
    try:
        import requests
        
        host = form_data.get("host", "sandbox.api.yodlee.com")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        api_version = form_data.get("api_version", "1.1")
        
        base_url = f"https://{host}/ysl/{api_version}"
        
        # Get API token
        response = requests.post(
            f"{base_url}/auth/token",
            data={
                "clientId": client_id,
                "secret": client_secret
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if "token" in data:
                return True, "Yodlee authentication successful"
        
        return False, f"Auth failed: HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Yodlee error: {str(e)}"

