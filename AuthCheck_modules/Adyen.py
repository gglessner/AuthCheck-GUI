"""Adyen Payment authentication module."""

module_description = "Adyen (Payment)"

form_fields = [
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["test", "live"], "default": "test"},
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "merchant_account", "type": "text", "label": "Merchant Account", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Adyen payment gateway. API key from Customer Area. Test vs Live endpoints differ."}
]

def authenticate(form_data):
    """Test Adyen authentication."""
    try:
        import requests
        
        environment = form_data.get("environment", "test")
        api_key = form_data.get("api_key", "")
        merchant_account = form_data.get("merchant_account", "")
        
        if environment == "test":
            base_url = "https://checkout-test.adyen.com/v70"
        else:
            base_url = "https://checkout-live.adyen.com/v70"
        
        response = requests.post(
            f"{base_url}/paymentMethods",
            json={
                "merchantAccount": merchant_account
            },
            headers={
                "X-API-Key": api_key,
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"Adyen authentication successful ({environment})"
        elif response.status_code == 401:
            return False, "Authentication failed - invalid API key"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, f"Adyen error: {str(e)}"

