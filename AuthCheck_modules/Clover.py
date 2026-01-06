"""Clover POS authentication module."""

module_description = "Clover (POS)"

form_fields = [
    {"name": "merchant_id", "type": "text", "label": "Merchant ID", "default": ""},
    {"name": "api_token", "type": "password", "label": "API Token", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Clover (Fiserv). API token from Clover Developer Dashboard."}
]

def authenticate(form_data):
    """Test Clover authentication."""
    try:
        import requests
        
        merchant_id = form_data.get("merchant_id", "")
        api_token = form_data.get("api_token", "")
        environment = form_data.get("environment", "sandbox")
        
        if environment == "sandbox":
            base_url = "https://sandbox.dev.clover.com"
        else:
            base_url = "https://api.clover.com"
        
        response = requests.get(
            f"{base_url}/v3/merchants/{merchant_id}",
            headers={"Authorization": f"Bearer {api_token}"},
            timeout=30
        )
        
        if response.status_code == 200:
            merchant = response.json()
            return True, f"Clover authentication successful ({merchant.get('name', merchant_id)})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Clover error: {str(e)}"

