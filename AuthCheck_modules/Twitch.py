"""Twitch API authentication module."""

module_description = "Twitch (Gaming)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "access_token", "type": "password", "label": "Access Token (optional)", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Register app at dev.twitch.tv. Client credentials for app tokens."}
]

def authenticate(form_data):
    """Test Twitch API authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        access_token = form_data.get("access_token", "")
        
        if not access_token:
            # Get app access token
            token_response = requests.post(
                "https://id.twitch.tv/oauth2/token",
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "grant_type": "client_credentials"
                },
                timeout=30
            )
            
            if token_response.status_code != 200:
                return False, f"Token request failed: {token_response.text}"
            
            access_token = token_response.json().get("access_token")
        
        # Validate token
        response = requests.get(
            "https://id.twitch.tv/oauth2/validate",
            headers={"Authorization": f"OAuth {access_token}"},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"Twitch API authentication successful"
        else:
            return False, f"Token validation failed"
            
    except Exception as e:
        return False, f"Twitch error: {str(e)}"

