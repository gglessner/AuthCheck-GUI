"""Webroot authentication module."""

module_description = "Webroot (EDR)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "api_secret", "type": "password", "label": "API Secret", "default": ""},
    {"name": "gsk_token", "type": "password", "label": "GSM Keycode", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Webroot. API credentials from Unity console > Settings > API Access."}
]

def authenticate(form_data):
    """Test Webroot authentication."""
    try:
        import requests
        
        api_key = form_data.get("api_key", "")
        api_secret = form_data.get("api_secret", "")
        gsk_token = form_data.get("gsk_token", "")
        
        # Get access token
        token_response = requests.post(
            "https://unityapi.webrootcloudav.com/auth/token",
            data={
                "grant_type": "password",
                "username": api_key,
                "password": api_secret,
                "scope": "Console.GSM"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        
        if token_response.status_code != 200:
            return False, f"Token error: HTTP {token_response.status_code}"
        
        access_token = token_response.json().get("access_token")
        
        response = requests.get(
            "https://unityapi.webrootcloudav.com/service/api/console/gsm",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Webroot authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Webroot error: {str(e)}"

