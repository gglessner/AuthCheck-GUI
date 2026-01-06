"""Coupa authentication module."""

module_description = "Coupa (Supply Chain)"

form_fields = [
    {"name": "instance", "type": "text", "label": "Instance URL", "default": ""},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "api_key", "type": "password", "label": "API Key (Legacy)", "default": ""},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["OAuth2", "API Key"], "default": "OAuth2"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Coupa BSM Platform. OAuth2 or legacy API key."}
]

def authenticate(form_data):
    """Test Coupa authentication."""
    try:
        import requests
        
        instance = form_data.get("instance", "").rstrip("/")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        api_key = form_data.get("api_key", "")
        auth_type = form_data.get("auth_type", "OAuth2")
        
        if auth_type == "OAuth2":
            # Get access token
            token_response = requests.post(
                f"{instance}/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scope": "core.common.read"
                },
                timeout=30
            )
            
            if token_response.status_code != 200:
                return False, f"Token error: {token_response.text}"
            
            access_token = token_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {access_token}"}
        else:
            headers = {"X-COUPA-API-KEY": api_key}
        
        response = requests.get(
            f"{instance}/api/users",
            headers=headers,
            params={"limit": 1},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Coupa authentication successful"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Coupa error: {str(e)}"

