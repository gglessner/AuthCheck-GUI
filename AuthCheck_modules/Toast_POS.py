"""Toast POS authentication module."""

module_description = "Toast (POS)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Toast API. OAuth2 credentials from Toast Developer Portal."}
]

def authenticate(form_data):
    """Test Toast POS authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        environment = form_data.get("environment", "sandbox")
        
        if environment == "sandbox":
            base_url = "https://ws-sandbox-api.toasttab.com"
        else:
            base_url = "https://ws-api.toasttab.com"
        
        response = requests.post(
            f"{base_url}/authentication/v1/authentication/login",
            json={
                "clientId": client_id,
                "clientSecret": client_secret,
                "userAccessType": "TOAST_MACHINE_CLIENT"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("token"):
                return True, f"Toast authentication successful ({environment})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        
        return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Toast error: {str(e)}"

