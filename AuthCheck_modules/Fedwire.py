"""Fedwire authentication module."""

module_description = "Fedwire (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "FedLine Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "User ID", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "aba_number", "type": "text", "label": "ABA Routing Number", "default": ""},
    {"name": "certificate", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.p12 *.pfx)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Fedwire via FedLine Direct. PKI certificate required."}
]

def authenticate(form_data):
    """Test Fedwire/FedLine authentication."""
    try:
        import requests
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        certificate = form_data.get("certificate", "")
        
        base_url = f"https://{host}:{port}"
        
        cert = certificate if certificate else None
        
        response = requests.get(
            f"{base_url}/api/health",
            auth=(username, password) if username else None,
            cert=cert,
            verify=True,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "FedLine authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Fedwire error: {str(e)}"

