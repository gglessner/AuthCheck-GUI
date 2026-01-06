"""Plaid authentication module."""

module_description = "Plaid (Payment)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "secret", "type": "password", "label": "Secret", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "development", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Plaid financial API. Credentials from dashboard.plaid.com."}
]

def authenticate(form_data):
    """Test Plaid authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        secret = form_data.get("secret", "")
        environment = form_data.get("environment", "sandbox")
        
        env_urls = {
            "sandbox": "https://sandbox.plaid.com",
            "development": "https://development.plaid.com",
            "production": "https://production.plaid.com"
        }
        base_url = env_urls.get(environment, env_urls["sandbox"])
        
        response = requests.post(
            f"{base_url}/institutions/get",
            json={
                "client_id": client_id,
                "secret": secret,
                "count": 1,
                "offset": 0,
                "country_codes": ["US"]
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"Plaid authentication successful ({environment})"
        elif response.status_code == 400:
            error = response.json()
            return False, f"Auth failed: {error.get('error_message', 'Unknown error')}"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Plaid error: {str(e)}"

