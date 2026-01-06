"""Tradier authentication module."""

module_description = "Tradier (Financial)"

form_fields = [
    {"name": "access_token", "type": "password", "label": "Access Token", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Tradier Brokerage API. Access token from developer.tradier.com"}
]

def authenticate(form_data):
    """Test Tradier authentication."""
    try:
        import requests
        
        access_token = form_data.get("access_token", "")
        environment = form_data.get("environment", "sandbox")
        
        if environment == "sandbox":
            base_url = "https://sandbox.tradier.com"
        else:
            base_url = "https://api.tradier.com"
        
        response = requests.get(
            f"{base_url}/v1/user/profile",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"Tradier authentication successful ({environment})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Tradier error: {str(e)}"

