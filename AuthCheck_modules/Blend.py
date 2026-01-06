"""Blend mortgage platform authentication module."""

module_description = "Blend (Financial)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Blend Labs. Digital mortgage platform. OAuth2."}
]

def authenticate(form_data):
    """Test Blend authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        environment = form_data.get("environment", "sandbox")
        
        if environment == "sandbox":
            base_url = "https://api.beta.blendlabs.com"
        else:
            base_url = "https://api.blendlabs.com"
        
        response = requests.post(
            f"{base_url}/oauth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            },
            timeout=30
        )
        
        if response.status_code == 200 and response.json().get("access_token"):
            return True, f"Blend authentication successful ({environment})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Blend error: {str(e)}"

