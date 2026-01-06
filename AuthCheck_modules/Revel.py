"""Revel Systems POS authentication module."""

module_description = "Revel Systems (POS)"

form_fields = [
    {"name": "domain", "type": "text", "label": "Domain", "default": ""},
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "api_secret", "type": "password", "label": "API Secret", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Revel Systems. API credentials from Management Console > Integrations."}
]

def authenticate(form_data):
    """Test Revel Systems authentication."""
    try:
        import requests
        
        domain = form_data.get("domain", "")
        api_key = form_data.get("api_key", "")
        api_secret = form_data.get("api_secret", "")
        
        base_url = f"https://{domain}.revelup.com"
        
        response = requests.get(
            f"{base_url}/enterprise/Establishment/",
            headers={
                "API-AUTHENTICATION": f"{api_key}:{api_secret}",
                "Content-Type": "application/json"
            },
            params={"limit": 1},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Revel Systems authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Revel error: {str(e)}"

