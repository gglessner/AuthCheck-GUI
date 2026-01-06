"""Equifax API authentication module."""

module_description = "Equifax (Financial)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Equifax API. Register at developer.equifax.com."}
]

def authenticate(form_data):
    """Test Equifax API authentication."""
    try:
        import requests
        import base64
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        environment = form_data.get("environment", "sandbox")
        
        if environment == "sandbox":
            base_url = "https://api.sandbox.equifax.com"
        else:
            base_url = "https://api.equifax.com"
        
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        response = requests.post(
            f"{base_url}/v2/oauth/token",
            data={"grant_type": "client_credentials", "scope": "https://api.equifax.com"},
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            timeout=30
        )
        
        if response.status_code == 200 and "access_token" in response.json():
            return True, f"Equifax authentication successful ({environment})"
        else:
            return False, f"Auth failed: {response.text}"
            
    except Exception as e:
        return False, f"Equifax error: {str(e)}"

