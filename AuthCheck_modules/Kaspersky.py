"""Kaspersky authentication module."""

module_description = "Kaspersky (EDR)"

form_fields = [
    {"name": "host", "type": "text", "label": "KSC Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "13299"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Security Center", "Endpoint Security Cloud"], "default": "Security Center"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Kaspersky Security Center. Default port 13299. KLAdmin default user."}
]

def authenticate(form_data):
    """Test Kaspersky authentication."""
    try:
        import requests
        
        host = form_data.get("host", "")
        port = form_data.get("port", "13299")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        product = form_data.get("product", "Security Center")
        verify_ssl = form_data.get("verify_ssl", False)
        
        base_url = f"https://{host}:{port}"
        
        # KSC uses session-based auth
        session = requests.Session()
        
        response = session.post(
            f"{base_url}/api/v1.0/login",
            json={"user": username, "password": password},
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("PxgRetVal"):
                return True, f"Kaspersky {product} authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        
        return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Kaspersky error: {str(e)}"

