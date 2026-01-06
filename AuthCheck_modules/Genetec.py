"""Genetec Security Center authentication module."""

module_description = "Genetec Security Center (Video)"

form_fields = [
    {"name": "host", "type": "text", "label": "Directory Server", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "app_id", "type": "text", "label": "Application ID", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Genetec Security Center. Web SDK API. Default port 4590 for SDK."}
]

def authenticate(form_data):
    """Test Genetec Security Center authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        app_id = form_data.get("app_id", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}"
        
        headers = {}
        if app_id:
            headers["X-Application-Id"] = app_id
        
        response = requests.get(
            f"{base_url}/WebSdk/LogonState",
            auth=HTTPBasicAuth(username, password),
            headers=headers,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Genetec Security Center authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Genetec error: {str(e)}"

