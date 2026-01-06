"""Xero authentication module."""

module_description = "Xero (Accounting)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "refresh_token", "type": "password", "label": "Refresh Token", "default": ""},
    {"name": "tenant_id", "type": "text", "label": "Tenant ID", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Xero API. OAuth2 required. Get credentials from Xero Developer."}
]

def authenticate(form_data):
    """Test Xero authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        refresh_token = form_data.get("refresh_token", "")
        tenant_id = form_data.get("tenant_id", "")
        
        # Get access token
        token_response = requests.post(
            "https://identity.xero.com/connect/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": client_id,
                "client_secret": client_secret
            },
            timeout=30
        )
        
        if token_response.status_code != 200:
            return False, f"Token error: {token_response.text}"
        
        access_token = token_response.json().get("access_token")
        
        response = requests.get(
            "https://api.xero.com/api.xro/2.0/Organisation",
            headers={
                "Authorization": f"Bearer {access_token}",
                "xero-tenant-id": tenant_id
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Xero authentication successful"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Xero error: {str(e)}"

