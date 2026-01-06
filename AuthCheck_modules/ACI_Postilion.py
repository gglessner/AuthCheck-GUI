"""ACI Postilion payment switch authentication module."""

module_description = "ACI Postilion (ATM)"

form_fields = [
    {"name": "host", "type": "text", "label": "Postilion Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "component", "type": "combo", "label": "Component", "options": ["Office", "Realtime", "Manager"], "default": "Office"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "ACI Worldwide Postilion. ATM/POS switch. Office for management."}
]

def authenticate(form_data):
    """Test ACI Postilion authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        component = form_data.get("component", "Office")
        verify_ssl = form_data.get("verify_ssl", False)
        
        base_url = f"https://{host}:{port}"
        
        response = requests.get(
            f"{base_url}/postilion/api/status",
            auth=HTTPBasicAuth(username, password),
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"ACI Postilion {component} authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"ACI Postilion error: {str(e)}"

