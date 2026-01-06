"""Pipedrive CRM authentication module."""

module_description = "Pipedrive (CRM)"

form_fields = [
    {"name": "api_token", "type": "password", "label": "API Token", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Pipedrive. API token from Settings > Personal Preferences > API."}
]

def authenticate(form_data):
    """Test Pipedrive authentication."""
    try:
        import requests
        
        api_token = form_data.get("api_token", "")
        
        response = requests.get(
            "https://api.pipedrive.com/v1/users/me",
            params={"api_token": api_token},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                user = data.get("data", {})
                return True, f"Pipedrive authentication successful ({user.get('name', 'unknown')})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        
        return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Pipedrive error: {str(e)}"

