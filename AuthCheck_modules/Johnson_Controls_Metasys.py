"""Johnson Controls Metasys authentication module."""

module_description = "Johnson Controls Metasys (ICS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Metasys Server", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Metasys BAS. REST API on /api/v1/. Default users vary by installation."}
]

def authenticate(form_data):
    """Test Johnson Controls Metasys authentication."""
    try:
        import requests
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", False)
        
        base_url = f"https://{host}:{port}"
        
        # Login to get token
        response = requests.post(
            f"{base_url}/api/v1/login",
            json={"username": username, "password": password},
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("accessToken"):
                return True, "Metasys authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        
        return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Metasys error: {str(e)}"

