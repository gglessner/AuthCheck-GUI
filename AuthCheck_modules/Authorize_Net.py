"""Authorize.Net authentication module."""

module_description = "Authorize.Net (Payment)"

form_fields = [
    {"name": "api_login_id", "type": "text", "label": "API Login ID", "default": ""},
    {"name": "transaction_key", "type": "password", "label": "Transaction Key", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Authorize.Net (Visa). Credentials from Merchant Interface."}
]

def authenticate(form_data):
    """Test Authorize.Net authentication."""
    try:
        import requests
        
        api_login_id = form_data.get("api_login_id", "")
        transaction_key = form_data.get("transaction_key", "")
        environment = form_data.get("environment", "sandbox")
        
        if environment == "sandbox":
            base_url = "https://apitest.authorize.net/xml/v1/request.api"
        else:
            base_url = "https://api.authorize.net/xml/v1/request.api"
        
        request_data = {
            "authenticateTestRequest": {
                "merchantAuthentication": {
                    "name": api_login_id,
                    "transactionKey": transaction_key
                }
            }
        }
        
        response = requests.post(
            base_url,
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            # Check for success in response
            text = response.text
            if "Ok" in text or "resultCode" in text:
                return True, f"Authorize.Net authentication successful ({environment})"
            else:
                return False, f"Auth failed: {text[:200]}"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Authorize.Net error: {str(e)}"

