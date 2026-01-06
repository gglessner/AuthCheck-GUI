"""Freshsales CRM authentication module."""

module_description = "Freshsales (CRM)"

form_fields = [
    {"name": "domain", "type": "text", "label": "Domain", "default": ""},
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Freshsales (Freshworks). API key from Settings > API Settings."}
]

def authenticate(form_data):
    """Test Freshsales authentication."""
    try:
        import requests
        
        domain = form_data.get("domain", "")
        api_key = form_data.get("api_key", "")
        
        response = requests.get(
            f"https://{domain}.freshsales.io/api/selector/owners",
            headers={"Authorization": f"Token token={api_key}"},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Freshsales authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Freshsales error: {str(e)}"

