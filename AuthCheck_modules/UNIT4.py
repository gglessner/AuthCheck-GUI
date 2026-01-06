"""Unit4 ERP authentication module."""

module_description = "Unit4 / Agresso (ERP)"

form_fields = [
    {"name": "host", "type": "text", "label": "Unit4 Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "client", "type": "text", "label": "Client", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Unit4 (Agresso). Web services authentication."}
]

def authenticate(form_data):
    """Test Unit4 authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        client = form_data.get("client", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}"
        
        headers = {}
        if client:
            headers["X-Client"] = client
        
        response = requests.get(
            f"{base_url}/api/v1/system/info",
            auth=HTTPBasicAuth(username, password),
            headers=headers,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Unit4 authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Unit4 error: {str(e)}"

