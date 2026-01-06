"""Amadeus GDS authentication module."""

module_description = "Amadeus (Travel)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "API Key", "default": ""},
    {"name": "client_secret", "type": "password", "label": "API Secret", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["test", "production"], "default": "test"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Amadeus for Developers. Self-service API credentials."}
]

def authenticate(form_data):
    """Test Amadeus authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        environment = form_data.get("environment", "test")
        
        if environment == "test":
            base_url = "https://test.api.amadeus.com"
        else:
            base_url = "https://api.amadeus.com"
        
        response = requests.post(
            f"{base_url}/v1/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            },
            timeout=30
        )
        
        if response.status_code == 200 and response.json().get("access_token"):
            return True, f"Amadeus authentication successful ({environment})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Amadeus error: {str(e)}"

