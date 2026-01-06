"""Autodesk BIM 360 / ACC authentication module."""

module_description = "Autodesk BIM 360 / ACC (Construction)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "refresh_token", "type": "password", "label": "Refresh Token", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["BIM 360", "Autodesk Construction Cloud"], "default": "Autodesk Construction Cloud"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Autodesk Platform Services. OAuth2 from Autodesk Forge."}
]

def authenticate(form_data):
    """Test Autodesk BIM 360/ACC authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        refresh_token = form_data.get("refresh_token", "")
        
        # Get access token
        token_response = requests.post(
            "https://developer.api.autodesk.com/authentication/v2/token",
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
            "https://developer.api.autodesk.com/project/v1/hubs",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Autodesk BIM 360/ACC authentication successful"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Autodesk error: {str(e)}"

