"""nCino bank operating system authentication module."""

module_description = "nCino (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "nCino Host", "default": ""},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "security_token", "type": "password", "label": "Security Token", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "nCino. Built on Salesforce. OAuth2 or SOAP login."}
]

def authenticate(form_data):
    """Test nCino authentication."""
    try:
        import requests
        
        host = form_data.get("host", "").rstrip("/")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        security_token = form_data.get("security_token", "")
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        # Salesforce OAuth2 password grant
        response = requests.post(
            f"{base_url}/services/oauth2/token",
            data={
                "grant_type": "password",
                "client_id": client_id,
                "client_secret": client_secret,
                "username": username,
                "password": f"{password}{security_token}"
            },
            timeout=30
        )
        
        if response.status_code == 200 and response.json().get("access_token"):
            return True, "nCino authentication successful"
        elif response.status_code == 400:
            error = response.json().get("error_description", "Unknown error")
            return False, f"Auth failed: {error}"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"nCino error: {str(e)}"

