"""Yardi property management authentication module."""

module_description = "Yardi Voyager (Property)"

form_fields = [
    {"name": "host", "type": "text", "label": "Yardi Host", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "database", "type": "text", "label": "Database", "default": ""},
    {"name": "server_name", "type": "text", "label": "Server Name", "default": ""},
    {"name": "platform", "type": "combo", "label": "Platform", "options": ["Voyager", "RentCafe", "Breeze"], "default": "Voyager"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Yardi Voyager. API credentials from Yardi support."}
]

def authenticate(form_data):
    """Test Yardi authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "").rstrip("/")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        database = form_data.get("database", "")
        platform = form_data.get("platform", "Voyager")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        if platform == "RentCafe":
            response = requests.get(
                f"{base_url}/rentcafeapi.aspx",
                params={"requestType": "property", "apiToken": password},
                verify=verify_ssl,
                timeout=30
            )
        else:
            response = requests.get(
                f"{base_url}/webservices/itfresidentdata.asmx",
                auth=HTTPBasicAuth(username, password),
                verify=verify_ssl,
                timeout=30
            )
        
        if response.status_code == 200:
            return True, f"Yardi {platform} authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Yardi error: {str(e)}"

