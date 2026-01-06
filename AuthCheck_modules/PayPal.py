"""PayPal authentication module."""

module_description = "PayPal (Payment)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "live"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "PayPal REST API. Get credentials from PayPal Developer Dashboard."}
]

def authenticate(form_data):
    """Test PayPal authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        environment = form_data.get("environment", "sandbox")
        
        if environment == "sandbox":
            base_url = "https://api-m.sandbox.paypal.com"
        else:
            base_url = "https://api-m.paypal.com"
        
        # Get access token
        response = requests.post(
            f"{base_url}/v1/oauth2/token",
            data={"grant_type": "client_credentials"},
            auth=(client_id, client_secret),
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("access_token"):
                return True, f"PayPal authentication successful ({environment})"
        
        return False, f"Authentication failed: HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"PayPal error: {str(e)}"
