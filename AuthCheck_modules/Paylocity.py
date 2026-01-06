"""Paylocity authentication module."""

module_description = "Paylocity (HR)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "company_id", "type": "text", "label": "Company ID", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Paylocity Web Link API. OAuth2 client credentials flow."}
]

def authenticate(form_data):
    """Test Paylocity authentication."""
    try:
        import requests
        import base64
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        company_id = form_data.get("company_id", "")
        environment = form_data.get("environment", "sandbox")
        
        if environment == "sandbox":
            token_url = "https://apisandbox.paylocity.com/IdentityServer/connect/token"
            api_url = "https://apisandbox.paylocity.com/api"
        else:
            token_url = "https://api.paylocity.com/IdentityServer/connect/token"
            api_url = "https://api.paylocity.com/api"
        
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        token_response = requests.post(
            token_url,
            data={"grant_type": "client_credentials", "scope": "WebLinkAPI"},
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            timeout=30
        )
        
        if token_response.status_code == 200 and "access_token" in token_response.json():
            return True, f"Paylocity authentication successful ({environment})"
        else:
            return False, f"Auth failed: {token_response.text}"
            
    except Exception as e:
        return False, f"Paylocity error: {str(e)}"

