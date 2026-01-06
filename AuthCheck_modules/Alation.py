"""Alation Data Catalog authentication module."""

module_description = "Alation (BigData)"

form_fields = [
    {"name": "base_url", "type": "text", "label": "Alation URL", "default": "https://alation.example.com"},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["API Token", "Username/Password", "OAuth2"], "default": "API Token"},
    {"name": "api_token", "type": "password", "label": "API Token", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API tokens from Settings > API Access. Default admin account varies."}
]

def authenticate(form_data):
    """Test Alation authentication."""
    try:
        import requests
        
        base_url = form_data.get("base_url", "").rstrip("/")
        auth_type = form_data.get("auth_type", "API Token")
        api_token = form_data.get("api_token", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        headers = {}
        
        if auth_type == "API Token" and api_token:
            headers["Token"] = api_token
        elif auth_type == "Username/Password" and username:
            # Get session token
            login_response = requests.post(
                f"{base_url}/api/v1/login/",
                data={"username": username, "password": password},
                verify=verify_ssl,
                timeout=30
            )
            if login_response.status_code == 200:
                headers["Token"] = login_response.json().get("token")
            else:
                return False, f"Login failed: HTTP {login_response.status_code}"
        
        response = requests.get(
            f"{base_url}/api/v1/user/me/",
            headers=headers,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            user = response.json()
            return True, f"Alation authentication successful (User: {user.get('username', 'unknown')})"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Alation error: {str(e)}"

