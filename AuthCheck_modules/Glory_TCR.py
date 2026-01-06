"""Glory Teller Cash Recycler authentication module."""

module_description = "Glory TCR (ATM)"

form_fields = [
    {"name": "host", "type": "text", "label": "TCR Host/IP", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["GLR-100", "RBG-100", "USF-300", "CI-10"], "default": "GLR-100"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Glory cash recyclers. Common: admin / admin, service / service."}
]

def authenticate(form_data):
    """Test Glory TCR authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", False)
        
        base_url = f"https://{host}:{port}"
        
        session = requests.Session()
        response = session.post(
            f"{base_url}/api/login",
            json={"user": username, "password": password},
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("token") or data.get("success"):
                return True, "Glory TCR authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        
        # Try basic auth fallback
        response = requests.get(
            f"{base_url}/api/status",
            auth=HTTPBasicAuth(username, password),
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Glory TCR authentication successful"
        
        return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Glory TCR error: {str(e)}"

