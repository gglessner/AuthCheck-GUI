"""TransUnion API authentication module."""

module_description = "TransUnion (Financial)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "member_code", "type": "text", "label": "Member Code", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TransUnion API. Register at developer.transunion.com."}
]

def authenticate(form_data):
    """Test TransUnion API authentication."""
    try:
        import requests
        
        api_key = form_data.get("api_key", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        environment = form_data.get("environment", "sandbox")
        
        if environment == "sandbox":
            base_url = "https://api-sandbox.transunion.com"
        else:
            base_url = "https://api.transunion.com"
        
        response = requests.post(
            f"{base_url}/v1/oauth/token",
            data={
                "grant_type": "password",
                "username": username,
                "password": password
            },
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            timeout=30
        )
        
        if response.status_code == 200 and "access_token" in response.json():
            return True, f"TransUnion authentication successful ({environment})"
        else:
            return False, f"Auth failed: {response.text}"
            
    except Exception as e:
        return False, f"TransUnion error: {str(e)}"

