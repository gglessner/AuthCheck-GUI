"""Stripe authentication module."""

module_description = "Stripe (Payment)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key (Secret)", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Stripe API. Secret key starts with sk_test_ or sk_live_."}
]

def authenticate(form_data):
    """Test Stripe authentication."""
    try:
        import requests
        
        api_key = form_data.get("api_key", "")
        
        response = requests.get(
            "https://api.stripe.com/v1/balance",
            auth=(api_key, ""),
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            env = "test" if "sk_test_" in api_key else "live"
            return True, f"Stripe authentication successful ({env} mode)"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Stripe error: {str(e)}"
