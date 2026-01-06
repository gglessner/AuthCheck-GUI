"""Ellie Mae Encompass (ICE) mortgage authentication module."""

module_description = "Ellie Mae Encompass (Financial)"

form_fields = [
    {"name": "instance_id", "type": "text", "label": "Instance ID", "default": ""},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Encompass (ICE Mortgage). OAuth2 for API access."}
]

def authenticate(form_data):
    """Test Ellie Mae Encompass authentication."""
    try:
        import requests
        
        instance_id = form_data.get("instance_id", "")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        environment = form_data.get("environment", "sandbox")
        
        if environment == "sandbox":
            base_url = "https://api.elliemae.com"
        else:
            base_url = "https://api.elliemae.com"
        
        # OAuth2 password grant
        response = requests.post(
            f"{base_url}/oauth2/v1/token",
            data={
                "grant_type": "password",
                "username": f"{username}@encompass:{instance_id}",
                "password": password,
                "client_id": client_id,
                "client_secret": client_secret
            },
            timeout=30
        )
        
        if response.status_code == 200 and response.json().get("access_token"):
            return True, "Encompass authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Encompass error: {str(e)}"

