"""DocuSign authentication module."""

module_description = "DocuSign (Document)"

form_fields = [
    {"name": "integration_key", "type": "text", "label": "Integration Key", "default": ""},
    {"name": "secret_key", "type": "password", "label": "Secret Key", "default": ""},
    {"name": "account_id", "type": "text", "label": "Account ID", "default": ""},
    {"name": "user_id", "type": "text", "label": "User ID (GUID)", "default": ""},
    {"name": "private_key", "type": "file", "label": "RSA Private Key", "filter": "Key Files (*.pem *.key);;All Files (*)"},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["JWT", "Authorization Code"], "default": "JWT"},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["demo", "production"], "default": "demo"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "DocuSign eSignature API. JWT auth recommended for server apps."}
]

def authenticate(form_data):
    """Test DocuSign authentication."""
    try:
        import requests
        
        integration_key = form_data.get("integration_key", "")
        account_id = form_data.get("account_id", "")
        user_id = form_data.get("user_id", "")
        environment = form_data.get("environment", "demo")
        
        if environment == "demo":
            auth_server = "account-d.docusign.com"
            api_base = "demo.docusign.net"
        else:
            auth_server = "account.docusign.com"
            api_base = "docusign.net"
        
        # For JWT auth, would need to generate JWT token with private key
        # This is a simplified check using the userinfo endpoint
        
        # If we had an access token, we'd verify it like this:
        response = requests.get(
            f"https://{auth_server}/oauth/userinfo",
            headers={"Authorization": f"Bearer test"},
            timeout=30
        )
        
        # For now, just verify the account endpoint is reachable
        if response.status_code == 401:
            return False, "DocuSign reachable but authentication required (provide valid JWT credentials)"
        elif response.status_code == 200:
            return True, "DocuSign authentication successful"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"DocuSign error: {str(e)}"

