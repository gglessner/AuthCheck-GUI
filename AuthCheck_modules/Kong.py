"""Kong API Gateway authentication module."""

module_description = "Kong (Middleware)"

form_fields = [
    {"name": "admin_url", "type": "text", "label": "Admin API URL", "default": "http://localhost:8001"},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["None", "Key-Auth", "Basic Auth", "RBAC Token"], "default": "None"},
    {"name": "api_key", "type": "password", "label": "API Key/RBAC Token", "default": ""},
    {"name": "username", "type": "text", "label": "Username (Basic)", "default": ""},
    {"name": "password", "type": "password", "label": "Password (Basic)", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Admin API port 8001. Gateway port 8000. Enterprise uses RBAC."}
]

def authenticate(form_data):
    """Test Kong authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        admin_url = form_data.get("admin_url", "http://localhost:8001").rstrip("/")
        auth_type = form_data.get("auth_type", "None")
        api_key = form_data.get("api_key", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        headers = {}
        auth = None
        
        if auth_type == "Key-Auth" and api_key:
            headers["apikey"] = api_key
        elif auth_type == "Basic Auth" and username:
            auth = HTTPBasicAuth(username, password)
        elif auth_type == "RBAC Token" and api_key:
            headers["Kong-Admin-Token"] = api_key
        
        response = requests.get(
            f"{admin_url}/status",
            headers=headers,
            auth=auth,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return True, f"Kong authentication successful (Database: {data.get('database', {}).get('reachable', 'unknown')})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Kong error: {str(e)}"
