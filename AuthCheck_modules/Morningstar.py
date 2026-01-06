"""Morningstar API authentication module."""

module_description = "Morningstar (Financial)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Morningstar Direct/Web Services. API key from developer portal."}
]

def authenticate(form_data):
    """Test Morningstar API authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        api_key = form_data.get("api_key", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        environment = form_data.get("environment", "sandbox")
        
        if environment == "sandbox":
            base_url = "https://api-sandbox.morningstar.com"
        else:
            base_url = "https://api.morningstar.com"
        
        headers = {}
        if api_key:
            headers["apikey"] = api_key
        
        auth = HTTPBasicAuth(username, password) if username else None
        
        response = requests.get(
            f"{base_url}/v1/securities",
            auth=auth,
            headers=headers,
            params={"limit": 1},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"Morningstar authentication successful ({environment})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Morningstar error: {str(e)}"

