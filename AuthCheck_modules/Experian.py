"""Experian API authentication module."""

module_description = "Experian (Financial)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Experian API. Register at developer.experian.com."}
]

def authenticate(form_data):
    """Test Experian API authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        environment = form_data.get("environment", "sandbox")
        
        if environment == "sandbox":
            base_url = "https://sandbox-us-api.experian.com"
        else:
            base_url = "https://us-api.experian.com"
        
        response = requests.post(
            f"{base_url}/oauth2/v1/token",
            data={
                "grant_type": "password",
                "client_id": client_id,
                "client_secret": client_secret,
                "username": username,
                "password": password
            },
            timeout=30
        )
        
        if response.status_code == 200 and "access_token" in response.json():
            return True, f"Experian authentication successful ({environment})"
        else:
            return False, f"Auth failed: {response.text}"
            
    except Exception as e:
        return False, f"Experian error: {str(e)}"

