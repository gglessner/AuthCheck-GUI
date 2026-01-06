"""PaperCut print management authentication module."""

module_description = "PaperCut (Print)"

form_fields = [
    {"name": "host", "type": "text", "label": "PaperCut Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "9191"},
    {"name": "auth_token", "type": "password", "label": "Auth Token", "default": ""},
    {"name": "username", "type": "text", "label": "Admin Username (Alt)", "default": "admin"},
    {"name": "password", "type": "password", "label": "Admin Password (Alt)", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "PaperCut MF/NG. Default: admin / password. Port 9191."}
]

def authenticate(form_data):
    """Test PaperCut authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "9191")
        auth_token = form_data.get("auth_token", "")
        username = form_data.get("username", "admin")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", False)
        
        base_url = f"https://{host}:{port}"
        
        if auth_token:
            response = requests.get(
                f"{base_url}/api/health/version",
                headers={"Authorization": auth_token},
                verify=verify_ssl,
                timeout=30
            )
        else:
            response = requests.get(
                f"{base_url}/api/health/version",
                auth=HTTPBasicAuth(username, password),
                verify=verify_ssl,
                timeout=30
            )
        
        if response.status_code == 200:
            return True, "PaperCut authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"PaperCut error: {str(e)}"

