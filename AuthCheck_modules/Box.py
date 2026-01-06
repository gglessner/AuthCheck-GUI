"""Box authentication module."""

module_description = "Box (Collaboration)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "enterprise_id", "type": "text", "label": "Enterprise ID", "default": ""},
    {"name": "jwt_key_id", "type": "text", "label": "JWT Key ID", "default": ""},
    {"name": "private_key", "type": "file", "label": "Private Key", "filter": "Key Files (*.pem *.key);;All Files (*)"},
    {"name": "developer_token", "type": "password", "label": "Developer Token (Alt)", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Box Platform. JWT for server apps, OAuth2 for user apps."}
]

def authenticate(form_data):
    """Test Box authentication."""
    try:
        import requests
        
        developer_token = form_data.get("developer_token", "")
        
        if developer_token:
            # Simple token-based auth
            response = requests.get(
                "https://api.box.com/2.0/users/me",
                headers={"Authorization": f"Bearer {developer_token}"},
                timeout=30
            )
            
            if response.status_code == 200:
                user = response.json()
                return True, f"Box authentication successful ({user.get('name', 'unknown')})"
            elif response.status_code == 401:
                return False, "Authentication failed"
            else:
                return False, f"HTTP {response.status_code}"
        else:
            # JWT auth would require generating JWT and exchanging for token
            return False, "JWT authentication requires boxsdk library. Install with: pip install boxsdk[jwt]"
            
    except Exception as e:
        return False, f"Box error: {str(e)}"
