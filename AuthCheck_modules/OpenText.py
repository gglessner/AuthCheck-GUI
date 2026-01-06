"""OpenText Content Server authentication module."""

module_description = "OpenText (Document)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Content Server", "Documentum", "Extended ECM"], "default": "Content Server"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "OpenText. Admin/livelink for Content Server. dmadmin for Documentum."}
]

def authenticate(form_data):
    """Test OpenText authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        product = form_data.get("product", "Content Server")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}"
        
        if product == "Content Server":
            response = requests.post(
                f"{base_url}/otcs/cs.exe/api/v1/auth",
                data={"username": username, "password": password},
                verify=verify_ssl,
                timeout=30
            )
        elif product == "Documentum":
            response = requests.get(
                f"{base_url}/dctm-rest/repositories",
                auth=HTTPBasicAuth(username, password),
                verify=verify_ssl,
                timeout=30
            )
        else:
            response = requests.get(
                f"{base_url}/api/v1/nodes/0",
                auth=HTTPBasicAuth(username, password),
                verify=verify_ssl,
                timeout=30
            )
        
        if response.status_code == 200:
            return True, f"OpenText {product} authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"OpenText error: {str(e)}"

