"""Refinitiv/Reuters Eikon authentication module."""

module_description = "Refinitiv/Reuters (Financial)"

form_fields = [
    {"name": "app_key", "type": "password", "label": "App Key", "default": ""},
    {"name": "username", "type": "text", "label": "Username (RDP)", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "api_type", "type": "combo", "label": "API Type", "options": ["Eikon Data API", "Refinitiv Data Platform"], "default": "Refinitiv Data Platform"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Eikon requires desktop app. RDP uses OAuth2. App key from AppKey Generator."}
]

def authenticate(form_data):
    """Test Refinitiv/Reuters authentication."""
    try:
        import requests
        
        app_key = form_data.get("app_key", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        client_id = form_data.get("client_id", "")
        api_type = form_data.get("api_type", "Refinitiv Data Platform")
        
        if api_type == "Refinitiv Data Platform":
            # RDP OAuth2 authentication
            response = requests.post(
                "https://api.refinitiv.com/auth/oauth2/v1/token",
                data={
                    "grant_type": "password",
                    "username": username,
                    "password": password,
                    "client_id": client_id if client_id else app_key,
                    "scope": "trapi"
                },
                timeout=30
            )
            
            if response.status_code == 200 and "access_token" in response.json():
                return True, "Refinitiv Data Platform authentication successful"
            else:
                return False, f"RDP auth failed: {response.text}"
        else:
            # Eikon Data API (requires local proxy)
            response = requests.get(
                "http://localhost:9000/api/v1/handshake",
                headers={"x-tr-applicationid": app_key},
                timeout=5
            )
            
            if response.status_code == 200:
                return True, "Eikon Data API handshake successful"
            else:
                return False, f"Eikon connection failed (is Eikon running?)"
            
    except Exception as e:
        return False, f"Refinitiv error: {str(e)}"

