"""Proofpoint authentication module."""

module_description = "Proofpoint (Email Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "API Host", "default": "tap-api-v2.proofpoint.com"},
    {"name": "principal", "type": "text", "label": "Service Principal", "default": ""},
    {"name": "secret", "type": "password", "label": "Secret", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["TAP", "CASB", "TRAP", "Security Awareness", "Essentials"], "default": "TAP"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TAP API credentials from Settings > Connected Applications. Principal/Secret pair."}
]

def authenticate(form_data):
    """Test Proofpoint authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "tap-api-v2.proofpoint.com")
        principal = form_data.get("principal", "")
        secret = form_data.get("secret", "")
        
        base_url = f"https://{host}"
        
        # TAP API uses Basic auth with principal:secret
        response = requests.get(
            f"{base_url}/v2/siem/all",
            auth=HTTPBasicAuth(principal, secret),
            params={"format": "json", "sinceSeconds": 3600},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Proofpoint TAP authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed - invalid credentials"
        elif response.status_code == 403:
            return False, "Forbidden - check API permissions"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Proofpoint error: {str(e)}"

