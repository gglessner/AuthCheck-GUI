"""ADP authentication module."""

module_description = "ADP (HR)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "certificate", "type": "file", "label": "SSL Certificate", "filter": "Certificate Files (*.pem *.crt)"},
    {"name": "private_key", "type": "file", "label": "Private Key", "filter": "Key Files (*.pem *.key)"},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["uat", "production"], "default": "uat"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "ADP API. Requires app registration and SSL client certificate."}
]

def authenticate(form_data):
    """Test ADP authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        certificate = form_data.get("certificate", "")
        private_key = form_data.get("private_key", "")
        environment = form_data.get("environment", "uat")
        
        if environment == "uat":
            token_url = "https://iat-api.adp.com/auth/oauth/v2/token"
        else:
            token_url = "https://api.adp.com/auth/oauth/v2/token"
        
        cert = (certificate, private_key) if certificate and private_key else None
        
        response = requests.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            },
            cert=cert,
            timeout=30
        )
        
        if response.status_code == 200 and "access_token" in response.json():
            return True, f"ADP authentication successful ({environment})"
        else:
            return False, f"Auth failed: {response.text}"
            
    except Exception as e:
        return False, f"ADP error: {str(e)}"

