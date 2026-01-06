"""Mambu cloud banking authentication module."""

module_description = "Mambu (Financial)"

form_fields = [
    {"name": "tenant", "type": "text", "label": "Tenant", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "api_key", "type": "password", "label": "API Key (Alt)", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Mambu cloud banking. API key from Settings > API Consumers."}
]

def authenticate(form_data):
    """Test Mambu authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        tenant = form_data.get("tenant", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        api_key = form_data.get("api_key", "")
        
        base_url = f"https://{tenant}.mambu.com/api"
        
        if api_key:
            headers = {"apikey": api_key}
            auth = None
        else:
            headers = {}
            auth = HTTPBasicAuth(username, password)
        
        response = requests.get(
            f"{base_url}/users/current",
            auth=auth,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            user = response.json()
            return True, f"Mambu authentication successful ({user.get('username', 'unknown')})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Mambu error: {str(e)}"

