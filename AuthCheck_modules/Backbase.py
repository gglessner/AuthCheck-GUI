"""Backbase digital banking authentication module."""

module_description = "Backbase (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "Backbase Host", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "realm", "type": "text", "label": "Realm", "default": "backbase"},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Backbase. Digital banking. Uses Keycloak for auth."}
]

def authenticate(form_data):
    """Test Backbase authentication."""
    try:
        import requests
        
        host = form_data.get("host", "").rstrip("/")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        realm = form_data.get("realm", "backbase")
        client_id = form_data.get("client_id", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        # Backbase uses Keycloak
        response = requests.post(
            f"{base_url}/auth/realms/{realm}/protocol/openid-connect/token",
            data={
                "grant_type": "password",
                "client_id": client_id,
                "username": username,
                "password": password
            },
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200 and response.json().get("access_token"):
            return True, "Backbase authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Backbase error: {str(e)}"

