"""Microsoft Dynamics 365 authentication module."""

module_description = "Microsoft Dynamics 365 (ERP)"

form_fields = [
    {"name": "org_url", "type": "text", "label": "Organization URL", "default": ""},
    {"name": "tenant_id", "type": "text", "label": "Tenant ID", "default": ""},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Finance & Operations", "Business Central", "Sales", "Customer Service"], "default": "Finance & Operations"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "D365. OAuth2 via Azure AD. App registration required."}
]

def authenticate(form_data):
    """Test Microsoft Dynamics 365 authentication."""
    try:
        import requests
        
        org_url = form_data.get("org_url", "").rstrip("/")
        tenant_id = form_data.get("tenant_id", "")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        product = form_data.get("product", "Finance & Operations")
        
        # Get access token
        token_response = requests.post(
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": f"{org_url}/.default"
            },
            timeout=30
        )
        
        if token_response.status_code != 200:
            return False, f"Token request failed: {token_response.text}"
        
        access_token = token_response.json().get("access_token")
        
        # Test API
        if "Business Central" in product:
            api_url = f"{org_url}/api/v2.0/companies"
        else:
            api_url = f"{org_url}/data/$metadata"
        
        response = requests.get(
            api_url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"Dynamics 365 {product} authentication successful"
        else:
            return False, f"API error: HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Dynamics 365 error: {str(e)}"

