"""Collibra Data Catalog authentication module."""

module_description = "Collibra (BigData)"

form_fields = [
    {"name": "base_url", "type": "text", "label": "Collibra URL", "default": "https://collibra.example.com"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "api_version", "type": "combo", "label": "API Version", "options": ["v2", "v1"], "default": "v2"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: Admin/admin. API at /rest/2.0/ or /rest/1.0/"}
]

def authenticate(form_data):
    """Test Collibra authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        base_url = form_data.get("base_url", "").rstrip("/")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        api_version = form_data.get("api_version", "v2")
        verify_ssl = form_data.get("verify_ssl", True)
        
        api_path = "/rest/2.0" if api_version == "v2" else "/rest/1.0"
        
        response = requests.get(
            f"{base_url}{api_path}/users/current",
            auth=HTTPBasicAuth(username, password),
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            user = response.json()
            return True, f"Collibra authentication successful (User: {user.get('userName', 'unknown')})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Collibra error: {str(e)}"

