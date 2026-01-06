"""BlackRock Aladdin authentication module."""

module_description = "BlackRock Aladdin (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "Aladdin Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "BlackRock Aladdin. Enterprise investment/risk management."}
]

def authenticate(form_data):
    """Test BlackRock Aladdin authentication."""
    try:
        import requests
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}"
        
        if client_id and client_secret:
            response = requests.post(
                f"{base_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret
                },
                verify=verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200 and "access_token" in response.json():
                return True, "BlackRock Aladdin OAuth authentication successful"
        
        return False, "Authentication requires client credentials"
            
    except Exception as e:
        return False, f"Aladdin error: {str(e)}"

