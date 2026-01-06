"""Symantec/Broadcom DLP authentication module."""

module_description = "Symantec (DLP)"

form_fields = [
    {"name": "host", "type": "text", "label": "Enforce Server", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "8443"},
    {"name": "username", "type": "text", "label": "Username", "default": "Administrator"},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Symantec DLP Enforce. Default: Administrator. REST API port 8443."}
]

def authenticate(form_data):
    """Test Symantec DLP authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "8443")
        username = form_data.get("username", "Administrator")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", False)
        
        base_url = f"https://{host}:{port}"
        
        response = requests.get(
            f"{base_url}/ProtectManager/webservices/v2/incidents",
            auth=HTTPBasicAuth(username, password),
            params={"limit": 1},
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Symantec DLP authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Symantec DLP error: {str(e)}"

