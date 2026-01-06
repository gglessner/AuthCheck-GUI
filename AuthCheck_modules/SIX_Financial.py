"""SIX Financial Information authentication module."""

module_description = "SIX Financial (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "API Host", "default": "api.six-group.com"},
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "SIX Financial Information. Swiss exchange data, Valordata."}
]

def authenticate(form_data):
    """Test SIX Financial authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "api.six-group.com")
        api_key = form_data.get("api_key", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}"
        
        headers = {}
        if api_key:
            headers["X-Api-Key"] = api_key
        
        auth = HTTPBasicAuth(username, password) if username else None
        
        response = requests.get(
            f"{base_url}/api/v1/health",
            auth=auth,
            headers=headers,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "SIX Financial authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"SIX Financial error: {str(e)}"

