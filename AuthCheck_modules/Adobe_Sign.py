"""Adobe Sign authentication module."""

module_description = "Adobe Sign (Document)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "refresh_token", "type": "password", "label": "Refresh Token", "default": ""},
    {"name": "integration_key", "type": "password", "label": "Integration Key (Legacy)", "default": ""},
    {"name": "shard", "type": "combo", "label": "Shard", "options": ["na1", "na2", "na3", "na4", "eu1", "eu2", "jp1", "au1"], "default": "na1"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Adobe Sign (Acrobat Sign). OAuth2 or legacy integration key."}
]

def authenticate(form_data):
    """Test Adobe Sign authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        refresh_token = form_data.get("refresh_token", "")
        integration_key = form_data.get("integration_key", "")
        shard = form_data.get("shard", "na1")
        
        base_url = f"https://api.{shard}.adobesign.com"
        
        if integration_key:
            # Legacy integration key
            response = requests.get(
                f"{base_url}/api/rest/v6/users",
                headers={"Access-Token": integration_key},
                params={"pageSize": 1},
                timeout=30
            )
        else:
            # OAuth2 refresh token flow
            token_response = requests.post(
                f"{base_url}/oauth/v2/refresh",
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
            
            response = requests.get(
                f"{base_url}/api/rest/v6/users",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"pageSize": 1},
                timeout=30
            )
        
        if response.status_code == 200:
            return True, "Adobe Sign authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Adobe Sign error: {str(e)}"

