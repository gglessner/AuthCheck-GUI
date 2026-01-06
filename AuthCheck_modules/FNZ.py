"""FNZ wealth management authentication module."""

module_description = "FNZ (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "FNZ Host", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "FNZ. Platform for wealth managers and asset servicers."}
]

def authenticate(form_data):
    """Test FNZ authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "").rstrip("/")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        api_key = form_data.get("api_key", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        headers = {}
        if api_key:
            headers["X-API-Key"] = api_key
        
        response = requests.get(
            f"{base_url}/api/v1/status",
            auth=HTTPBasicAuth(username, password) if username else None,
            headers=headers,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "FNZ authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"FNZ error: {str(e)}"

