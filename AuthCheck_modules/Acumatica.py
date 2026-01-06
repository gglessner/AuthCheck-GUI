"""Acumatica ERP authentication module."""

module_description = "Acumatica (ERP)"

form_fields = [
    {"name": "host", "type": "text", "label": "Acumatica Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "company", "type": "text", "label": "Company", "default": ""},
    {"name": "branch", "type": "text", "label": "Branch", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Acumatica Cloud ERP. Cookie-based or OAuth2 authentication."}
]

def authenticate(form_data):
    """Test Acumatica authentication."""
    try:
        import requests
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        company = form_data.get("company", "")
        branch = form_data.get("branch", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}"
        
        login_data = {
            "name": username,
            "password": password
        }
        if company:
            login_data["company"] = company
        if branch:
            login_data["branch"] = branch
        
        session = requests.Session()
        response = session.post(
            f"{base_url}/entity/auth/login",
            json=login_data,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 204 or response.status_code == 200:
            # Logout
            session.post(f"{base_url}/entity/auth/logout", verify=verify_ssl)
            return True, "Acumatica authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Acumatica error: {str(e)}"

