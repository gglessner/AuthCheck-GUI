"""OneTrust authentication module."""

module_description = "OneTrust (Compliance)"

form_fields = [
    {"name": "host", "type": "text", "label": "OneTrust Host", "default": "app.onetrust.com"},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "OneTrust Privacy Platform. OAuth2 credentials from API Access settings."}
]

def authenticate(form_data):
    """Test OneTrust authentication."""
    try:
        import requests
        
        host = form_data.get("host", "app.onetrust.com")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        
        base_url = f"https://{host}"
        
        response = requests.post(
            f"{base_url}/api/access/v1/oauth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            },
            timeout=30
        )
        
        if response.status_code == 200 and "access_token" in response.json():
            return True, "OneTrust authentication successful"
        else:
            return False, f"Auth failed: {response.text}"
            
    except Exception as e:
        return False, f"OneTrust error: {str(e)}"

