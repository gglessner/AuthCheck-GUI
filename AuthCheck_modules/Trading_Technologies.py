"""Trading Technologies (TT) authentication module."""

module_description = "Trading Technologies (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "TT Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "app_key", "type": "password", "label": "App Key", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["UAT", "Production"], "default": "UAT"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Trading Technologies. TT REST API. App key from Setup app."}
]

def authenticate(form_data):
    """Test Trading Technologies authentication."""
    try:
        import requests
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        app_key = form_data.get("app_key", "")
        
        base_url = f"https://{host}:{port}"
        
        response = requests.post(
            f"{base_url}/ttrestapi/authenticate",
            json={
                "username": username,
                "password": password,
                "app_key": app_key
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Trading Technologies authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"TT error: {str(e)}"

