"""Sabre GDS authentication module."""

module_description = "Sabre (Travel)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["cert", "prod"], "default": "cert"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Sabre Dev Studio. OAuth2 credentials from developer portal."}
]

def authenticate(form_data):
    """Test Sabre authentication."""
    try:
        import requests
        import base64
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        environment = form_data.get("environment", "cert")
        
        if environment == "cert":
            base_url = "https://api-crt.cert.havail.sabre.com"
        else:
            base_url = "https://api.havail.sabre.com"
        
        # Base64 encode client credentials
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        response = requests.post(
            f"{base_url}/v2/auth/token",
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={"grant_type": "client_credentials"},
            timeout=30
        )
        
        if response.status_code == 200 and response.json().get("access_token"):
            return True, f"Sabre authentication successful ({environment})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Sabre error: {str(e)}"

