"""Epic Games API authentication module."""

module_description = "Epic Games (Gaming)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "deployment_id", "type": "text", "label": "Deployment ID", "default": ""},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["Client Credentials", "Authorization Code"], "default": "Client Credentials"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Register app at dev.epicgames.com/portal. Uses OAuth2."}
]

def authenticate(form_data):
    """Test Epic Games API authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        
        response = requests.post(
            "https://api.epicgames.dev/epic/oauth/v1/token",
            data={
                "grant_type": "client_credentials",
                "scope": "basic_profile"
            },
            auth=HTTPBasicAuth(client_id, client_secret),
            timeout=30
        )
        
        if response.status_code == 200 and "access_token" in response.json():
            return True, "Epic Games API authentication successful"
        else:
            return False, f"Auth failed: {response.text}"
            
    except Exception as e:
        return False, f"Epic Games error: {str(e)}"

