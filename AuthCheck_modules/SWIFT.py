"""SWIFT Alliance authentication module."""

module_description = "SWIFT (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "Alliance Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "bic", "type": "text", "label": "BIC Code", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "certificate", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.pem *.p12 *.pfx)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "SWIFT uses PKI authentication. BIC = Bank Identifier Code (8 or 11 chars)."}
]

def authenticate(form_data):
    """Test SWIFT Alliance access."""
    try:
        import requests
        
        host = form_data.get("host", "localhost")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        certificate = form_data.get("certificate", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}"
        
        cert = certificate if certificate else None
        auth = (username, password) if username else None
        
        response = requests.get(
            f"{base_url}/swift/api/v1/health",
            auth=auth,
            cert=cert,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"SWIFT Alliance accessible at {host}"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"SWIFT error: {str(e)}"

