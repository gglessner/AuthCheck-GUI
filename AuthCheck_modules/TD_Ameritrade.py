"""TD Ameritrade/Schwab authentication module."""

module_description = "TD Ameritrade/Schwab (Financial)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID (API Key)", "default": ""},
    {"name": "refresh_token", "type": "password", "label": "Refresh Token", "default": ""},
    {"name": "redirect_uri", "type": "text", "label": "Redirect URI", "default": "https://localhost"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TD Ameritrade API (now Schwab). OAuth2 flow. Register at developer.tdameritrade.com"}
]

def authenticate(form_data):
    """Test TD Ameritrade authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        refresh_token = form_data.get("refresh_token", "")
        
        if not refresh_token:
            return False, "Refresh token required (OAuth2 flow)"
        
        response = requests.post(
            "https://api.tdameritrade.com/v1/oauth2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": f"{client_id}@AMER.OAUTHAP"
            },
            timeout=30
        )
        
        if response.status_code == 200 and "access_token" in response.json():
            return True, "TD Ameritrade authentication successful"
        else:
            return False, f"Auth failed: {response.text}"
            
    except Exception as e:
        return False, f"TD Ameritrade error: {str(e)}"

