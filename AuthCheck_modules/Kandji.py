"""Kandji authentication module."""

module_description = "Kandji (MDM)"

form_fields = [
    {"name": "subdomain", "type": "text", "label": "Subdomain", "default": ""},
    {"name": "api_token", "type": "password", "label": "API Token", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Kandji MDM. API token from Settings > Access > API Token."}
]

def authenticate(form_data):
    """Test Kandji authentication."""
    try:
        import requests
        
        subdomain = form_data.get("subdomain", "")
        api_token = form_data.get("api_token", "")
        
        base_url = f"https://{subdomain}.api.kandji.io"
        
        response = requests.get(
            f"{base_url}/api/v1/devices",
            headers={"Authorization": f"Bearer {api_token}"},
            params={"limit": 1},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Kandji authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed - invalid token"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Kandji error: {str(e)}"

