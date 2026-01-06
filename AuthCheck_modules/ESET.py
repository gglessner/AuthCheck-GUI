"""ESET authentication module."""

module_description = "ESET (EDR)"

form_fields = [
    {"name": "host", "type": "text", "label": "ESET PROTECT Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["PROTECT Cloud", "PROTECT On-prem", "Security Management Center"], "default": "PROTECT Cloud"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "ESET PROTECT. Default: Administrator. Web console on port 443."}
]

def authenticate(form_data):
    """Test ESET authentication."""
    try:
        import requests
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        product = form_data.get("product", "PROTECT Cloud")
        verify_ssl = form_data.get("verify_ssl", True)
        
        if product == "PROTECT Cloud":
            base_url = f"https://{host}"
        else:
            base_url = f"https://{host}:{port}"
        
        # Login to get session
        session = requests.Session()
        response = session.post(
            f"{base_url}/api/v1/login",
            json={"username": username, "password": password},
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("token") or data.get("success"):
                return True, f"ESET {product} authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        
        return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"ESET error: {str(e)}"

