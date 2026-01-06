"""SAP Ariba authentication module."""

module_description = "SAP Ariba (Supply Chain)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "secret", "type": "password", "label": "Shared Secret", "default": ""},
    {"name": "realm", "type": "text", "label": "Realm (AN ID)", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "SAP Ariba. API key from Ariba Developer Portal."}
]

def authenticate(form_data):
    """Test SAP Ariba authentication."""
    try:
        import requests
        
        api_key = form_data.get("api_key", "")
        realm = form_data.get("realm", "")
        environment = form_data.get("environment", "sandbox")
        
        if environment == "sandbox":
            base_url = "https://openapi.ariba.com"
        else:
            base_url = "https://openapi.ariba.com"
        
        response = requests.get(
            f"{base_url}/api/procurement-reporting/v2/prod/views/ViewName",
            headers={"apiKey": api_key},
            params={"realm": realm, "$top": 1},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "SAP Ariba authentication successful"
        elif response.status_code in [401, 403]:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"SAP Ariba error: {str(e)}"

