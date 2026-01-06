"""Xbox Live API authentication module."""

module_description = "Xbox Live (Gaming)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Azure App Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "refresh_token", "type": "password", "label": "Refresh Token", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Register app in Azure AD. Requires Xbox Live scope permissions."}
]

def authenticate(form_data):
    """Test Xbox Live authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        refresh_token = form_data.get("refresh_token", "")
        
        if not refresh_token:
            return False, "Refresh token required for Xbox Live authentication"
        
        # Exchange refresh token for access token
        token_response = requests.post(
            "https://login.live.com/oauth20_token.srf",
            data={
                "grant_type": "refresh_token",
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "scope": "Xboxlive.signin Xboxlive.offline_access"
            },
            timeout=30
        )
        
        if token_response.status_code != 200:
            return False, f"Token refresh failed: {token_response.text}"
        
        access_token = token_response.json().get("access_token")
        
        # Authenticate with Xbox Live
        xbl_response = requests.post(
            "https://user.auth.xboxlive.com/user/authenticate",
            json={
                "Properties": {
                    "AuthMethod": "RPS",
                    "SiteName": "user.auth.xboxlive.com",
                    "RpsTicket": f"d={access_token}"
                },
                "RelyingParty": "http://auth.xboxlive.com",
                "TokenType": "JWT"
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if xbl_response.status_code == 200:
            return True, "Xbox Live authentication successful"
        else:
            return False, f"Xbox Live auth failed: {xbl_response.text}"
            
    except Exception as e:
        return False, f"Xbox Live error: {str(e)}"

