"""Alpaca Trading authentication module."""

module_description = "Alpaca (Financial)"

form_fields = [
    {"name": "api_key", "type": "text", "label": "API Key ID", "default": ""},
    {"name": "secret_key", "type": "password", "label": "Secret Key", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["paper", "live"], "default": "paper"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Alpaca Trading. Paper: paper-api.alpaca.markets, Live: api.alpaca.markets"}
]

def authenticate(form_data):
    """Test Alpaca authentication."""
    try:
        import requests
        
        api_key = form_data.get("api_key", "")
        secret_key = form_data.get("secret_key", "")
        environment = form_data.get("environment", "paper")
        
        if environment == "paper":
            base_url = "https://paper-api.alpaca.markets"
        else:
            base_url = "https://api.alpaca.markets"
        
        response = requests.get(
            f"{base_url}/v2/account",
            headers={
                "APCA-API-KEY-ID": api_key,
                "APCA-API-SECRET-KEY": secret_key
            },
            timeout=30
        )
        
        if response.status_code == 200:
            account = response.json()
            return True, f"Alpaca authentication successful (Account: {account.get('account_number')})"
        elif response.status_code == 401:
            return False, "Authentication failed - invalid credentials"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Alpaca error: {str(e)}"

