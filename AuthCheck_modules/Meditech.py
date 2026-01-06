"""Meditech EHR authentication module."""

module_description = "Meditech (Healthcare)"

form_fields = [
    {"name": "host", "type": "text", "label": "Meditech Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "mnemonic", "type": "text", "label": "Hospital Mnemonic", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Meditech Expanse uses web interface. Legacy uses M-AT protocol."}
]

def authenticate(form_data):
    """Test Meditech authentication."""
    try:
        import requests
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        mnemonic = form_data.get("mnemonic", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}"
        
        # Try web login
        session = requests.Session()
        
        login_response = session.post(
            f"{base_url}/login",
            data={
                "username": username,
                "password": password,
                "mnemonic": mnemonic
            },
            verify=verify_ssl,
            timeout=30
        )
        
        if login_response.status_code == 200:
            return True, "Meditech web authentication successful"
        elif login_response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {login_response.status_code}"
            
    except Exception as e:
        return False, f"Meditech error: {str(e)}"

