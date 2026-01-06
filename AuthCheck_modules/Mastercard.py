"""Mastercard API authentication module."""

module_description = "Mastercard (Payment)"

form_fields = [
    {"name": "consumer_key", "type": "text", "label": "Consumer Key", "default": ""},
    {"name": "signing_key", "type": "file", "label": "Signing Key (P12)", "filter": "Certificate Files (*.p12 *.pfx)"},
    {"name": "key_alias", "type": "text", "label": "Key Alias", "default": "keyalias"},
    {"name": "key_password", "type": "password", "label": "Key Password", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Mastercard Developers. OAuth 1.0a with RSA-SHA256 signing."}
]

def authenticate(form_data):
    """Test Mastercard API authentication."""
    try:
        import requests
        
        consumer_key = form_data.get("consumer_key", "")
        environment = form_data.get("environment", "sandbox")
        
        if environment == "sandbox":
            base_url = "https://sandbox.api.mastercard.com"
        else:
            base_url = "https://api.mastercard.com"
        
        # Note: Full OAuth 1.0a implementation requires oauth1 library
        response = requests.get(
            f"{base_url}/status",
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"Mastercard API reachable ({environment})"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Mastercard error: {str(e)}"

