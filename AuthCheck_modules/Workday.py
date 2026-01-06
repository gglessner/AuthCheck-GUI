"""Workday authentication module."""

module_description = "Workday (HR)"

form_fields = [
    {"name": "tenant", "type": "text", "label": "Tenant", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "client_id", "type": "text", "label": "Client ID (OAuth)", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "refresh_token", "type": "password", "label": "Refresh Token", "default": ""},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["Basic", "OAuth2"], "default": "Basic"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Workday. ISU username format: ISU_username@tenant. OAuth preferred."}
]

def authenticate(form_data):
    """Test Workday authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        tenant = form_data.get("tenant", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        refresh_token = form_data.get("refresh_token", "")
        auth_type = form_data.get("auth_type", "Basic")
        
        base_url = f"https://wd2-impl-services1.workday.com/ccx/api/v1/{tenant}"
        
        if auth_type == "OAuth2":
            # Get access token
            token_response = requests.post(
                f"https://wd2-impl-services1.workday.com/ccx/oauth2/{tenant}/token",
                data={
                    "grant_type": "refresh_token",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token
                },
                timeout=30
            )
            
            if token_response.status_code != 200:
                return False, f"Token error: {token_response.text}"
            
            access_token = token_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {access_token}"}
            auth = None
        else:
            headers = {}
            auth = HTTPBasicAuth(f"{username}@{tenant}", password)
        
        response = requests.get(
            f"{base_url}/workers",
            auth=auth,
            headers=headers,
            params={"limit": 1},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Workday authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Workday error: {str(e)}"
