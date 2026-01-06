"""AppFolio property management authentication module."""

module_description = "AppFolio (Property)"

form_fields = [
    {"name": "database_name", "type": "text", "label": "Database Name", "default": ""},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "AppFolio. API credentials from Integration Partner Portal."}
]

def authenticate(form_data):
    """Test AppFolio authentication."""
    try:
        import requests
        
        database_name = form_data.get("database_name", "")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        
        response = requests.post(
            f"https://{database_name}.appfolio.com/api/v1/auth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            },
            timeout=30
        )
        
        if response.status_code == 200 and response.json().get("access_token"):
            return True, "AppFolio authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"AppFolio error: {str(e)}"

