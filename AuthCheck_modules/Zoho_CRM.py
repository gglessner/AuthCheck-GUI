"""Zoho CRM authentication module."""

module_description = "Zoho CRM (CRM)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "refresh_token", "type": "password", "label": "Refresh Token", "default": ""},
    {"name": "region", "type": "combo", "label": "Region", "options": ["com", "eu", "in", "com.au", "com.cn", "jp"], "default": "com"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Zoho CRM API. OAuth2 credentials from Zoho Developer Console."}
]

def authenticate(form_data):
    """Test Zoho CRM authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        refresh_token = form_data.get("refresh_token", "")
        region = form_data.get("region", "com")
        
        # Get access token
        token_response = requests.post(
            f"https://accounts.zoho.{region}/oauth/v2/token",
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
            f"https://www.zohoapis.{region}/crm/v3/users?type=CurrentUser",
            headers={"Authorization": f"Zoho-oauthtoken {access_token}"},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Zoho CRM authentication successful"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Zoho CRM error: {str(e)}"

