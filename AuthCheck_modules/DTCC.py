"""DTCC authentication module."""

module_description = "DTCC (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "DTCC Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "User ID", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "participant_id", "type": "text", "label": "Participant ID", "default": ""},
    {"name": "certificate", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.p12 *.pfx)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "DTCC clearing services. Requires participant registration."}
]

def authenticate(form_data):
    """Test DTCC authentication."""
    try:
        import requests
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        certificate = form_data.get("certificate", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}"
        
        cert = certificate if certificate else None
        
        response = requests.post(
            f"{base_url}/api/v1/auth",
            json={"userId": username, "password": password},
            cert=cert,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "DTCC authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"DTCC error: {str(e)}"

