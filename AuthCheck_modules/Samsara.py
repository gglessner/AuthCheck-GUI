"""Samsara fleet management authentication module."""

module_description = "Samsara (Fleet)"

form_fields = [
    {"name": "api_token", "type": "password", "label": "API Token", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Samsara. API token from Settings > API Tokens."}
]

def authenticate(form_data):
    """Test Samsara authentication."""
    try:
        import requests
        
        api_token = form_data.get("api_token", "")
        
        response = requests.get(
            "https://api.samsara.com/v1/me",
            headers={"Authorization": f"Bearer {api_token}"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return True, f"Samsara authentication successful ({data.get('data', {}).get('name', 'unknown')})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Samsara error: {str(e)}"

