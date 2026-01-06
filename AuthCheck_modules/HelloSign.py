"""HelloSign (Dropbox Sign) authentication module."""

module_description = "HelloSign / Dropbox Sign (Document)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "HelloSign/Dropbox Sign. API key from Settings > Integrations > API."}
]

def authenticate(form_data):
    """Test HelloSign authentication."""
    try:
        import requests
        
        api_key = form_data.get("api_key", "")
        
        response = requests.get(
            "https://api.hellosign.com/v3/account",
            auth=(api_key, ""),
            timeout=30
        )
        
        if response.status_code == 200:
            account = response.json().get("account", {})
            return True, f"HelloSign authentication successful ({account.get('email_address', 'unknown')})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"HelloSign error: {str(e)}"

