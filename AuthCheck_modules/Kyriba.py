"""Kyriba Treasury authentication module."""

module_description = "Kyriba (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "app.kyriba.com"},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "company_code", "type": "text", "label": "Company Code", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Kyriba cloud treasury management. app.kyriba.com for cloud."}
]

def authenticate(form_data):
    """Test Kyriba authentication."""
    try:
        import requests
        
        host = form_data.get("host", "app.kyriba.com")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        company_code = form_data.get("company_code", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}"
        
        response = requests.post(
            f"{base_url}/api/auth/login",
            json={
                "username": username,
                "password": password,
                "companyCode": company_code
            },
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Kyriba authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Kyriba error: {str(e)}"

