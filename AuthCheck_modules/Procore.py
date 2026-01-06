"""Procore construction management authentication module."""

module_description = "Procore (Construction)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "refresh_token", "type": "password", "label": "Refresh Token", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Procore. OAuth2 from developer.procore.com."}
]

def authenticate(form_data):
    """Test Procore authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        refresh_token = form_data.get("refresh_token", "")
        environment = form_data.get("environment", "sandbox")
        
        if environment == "sandbox":
            base_url = "https://sandbox.procore.com"
        else:
            base_url = "https://api.procore.com"
        
        # Get access token
        token_response = requests.post(
            f"{base_url}/oauth/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret
            },
            timeout=30
        )
        
        if token_response.status_code != 200:
            return False, f"Token error: {token_response.text}"
        
        access_token = token_response.json().get("access_token")
        
        response = requests.get(
            f"{base_url}/rest/v1.0/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Procore authentication successful"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Procore error: {str(e)}"

