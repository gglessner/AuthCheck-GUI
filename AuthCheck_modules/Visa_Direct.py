"""Visa Direct authentication module."""

module_description = "Visa Direct (Payment)"

form_fields = [
    {"name": "user_id", "type": "text", "label": "User ID", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "certificate", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.p12)"},
    {"name": "private_key", "type": "file", "label": "Private Key", "filter": "Key Files (*.pem *.key)"},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["sandbox", "production"], "default": "sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Visa Developer Platform. Two-way SSL required."}
]

def authenticate(form_data):
    """Test Visa Direct authentication."""
    try:
        import requests
        
        user_id = form_data.get("user_id", "")
        password = form_data.get("password", "")
        certificate = form_data.get("certificate", "")
        private_key = form_data.get("private_key", "")
        environment = form_data.get("environment", "sandbox")
        
        if environment == "sandbox":
            base_url = "https://sandbox.api.visa.com"
        else:
            base_url = "https://api.visa.com"
        
        cert = (certificate, private_key) if certificate and private_key else None
        
        response = requests.get(
            f"{base_url}/vdp/helloworld",
            auth=(user_id, password),
            cert=cert,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"Visa Direct authentication successful ({environment})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Visa Direct error: {str(e)}"

