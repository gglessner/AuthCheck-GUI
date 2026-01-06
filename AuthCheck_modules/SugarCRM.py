"""SugarCRM authentication module."""

module_description = "SugarCRM (CRM)"

form_fields = [
    {"name": "host", "type": "text", "label": "Sugar Host", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "client_id", "type": "text", "label": "OAuth Client ID", "default": "sugar"},
    {"name": "platform", "type": "text", "label": "Platform", "default": "base"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "SugarCRM. Default: admin / admin. Platform: base, mobile, portal."}
]

def authenticate(form_data):
    """Test SugarCRM authentication."""
    try:
        import requests
        
        host = form_data.get("host", "").rstrip("/")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        client_id = form_data.get("client_id", "sugar")
        platform = form_data.get("platform", "base")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        response = requests.post(
            f"{base_url}/rest/v11_12/oauth2/token",
            json={
                "grant_type": "password",
                "client_id": client_id,
                "username": username,
                "password": password,
                "platform": platform
            },
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200 and response.json().get("access_token"):
            return True, "SugarCRM authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"SugarCRM error: {str(e)}"

