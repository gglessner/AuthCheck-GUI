"""QuickBooks authentication module."""

module_description = "QuickBooks (Accounting)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "refresh_token", "type": "password", "label": "Refresh Token", "default": ""},
    {"name": "realm_id", "type": "text", "label": "Company/Realm ID", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "QuickBooks Online API. OAuth2 required. Get credentials from Intuit Developer."}
]

def authenticate(form_data):
    """Test QuickBooks authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        refresh_token = form_data.get("refresh_token", "")
        realm_id = form_data.get("realm_id", "")
        environment = form_data.get("environment", "sandbox")
        
        # Get access token
        token_response = requests.post(
            "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            },
            auth=(client_id, client_secret),
            timeout=30
        )
        
        if token_response.status_code != 200:
            return False, f"Token error: {token_response.text}"
        
        access_token = token_response.json().get("access_token")
        
        if environment == "sandbox":
            base_url = "https://sandbox-quickbooks.api.intuit.com"
        else:
            base_url = "https://quickbooks.api.intuit.com"
        
        response = requests.get(
            f"{base_url}/v3/company/{realm_id}/companyinfo/{realm_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30
        )
        
        if response.status_code == 200:
            company = response.json().get("CompanyInfo", {}).get("CompanyName", realm_id)
            return True, f"QuickBooks authentication successful ({company})"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"QuickBooks error: {str(e)}"

