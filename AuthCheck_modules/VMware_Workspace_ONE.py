"""VMware Workspace ONE authentication module."""

module_description = "VMware Workspace ONE (MDM)"

form_fields = [
    {"name": "host", "type": "text", "label": "API Host", "default": "as###.awmdm.com"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "api_key", "type": "password", "label": "API Key (aw-tenant-code)", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "AirWatch/Workspace ONE UEM. API key from Groups & Settings > System > Advanced > API."}
]

def authenticate(form_data):
    """Test VMware Workspace ONE authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        api_key = form_data.get("api_key", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}"
        
        headers = {
            "aw-tenant-code": api_key,
            "Accept": "application/json"
        }
        
        response = requests.get(
            f"{base_url}/api/system/info",
            auth=HTTPBasicAuth(username, password),
            headers=headers,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            info = response.json()
            return True, f"Workspace ONE authentication successful (v{info.get('ProductVersion', 'unknown')})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Workspace ONE error: {str(e)}"

