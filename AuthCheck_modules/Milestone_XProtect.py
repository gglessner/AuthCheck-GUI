"""Milestone XProtect authentication module."""

module_description = "Milestone XProtect (Video)"

form_fields = [
    {"name": "host", "type": "text", "label": "Management Server", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "domain", "type": "text", "label": "Domain (optional)", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Milestone XProtect VMS. REST API. Windows or basic auth."}
]

def authenticate(form_data):
    """Test Milestone XProtect authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        domain = form_data.get("domain", "")
        verify_ssl = form_data.get("verify_ssl", False)
        
        base_url = f"https://{host}:{port}"
        
        full_username = f"{domain}\\{username}" if domain else username
        
        response = requests.get(
            f"{base_url}/IDP/connect/authorize",
            auth=HTTPBasicAuth(full_username, password),
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code in [200, 302]:
            return True, "Milestone XProtect authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Milestone error: {str(e)}"

