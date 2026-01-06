"""PandaDoc authentication module."""

module_description = "PandaDoc (Document)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "PandaDoc. API key from Settings > Integrations > API."}
]

def authenticate(form_data):
    """Test PandaDoc authentication."""
    try:
        import requests
        
        api_key = form_data.get("api_key", "")
        
        response = requests.get(
            "https://api.pandadoc.com/public/v1/documents",
            headers={"Authorization": f"API-Key {api_key}"},
            params={"count": 1},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "PandaDoc authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"PandaDoc error: {str(e)}"

