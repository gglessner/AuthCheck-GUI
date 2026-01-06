"""Oracle JD Edwards authentication module."""

module_description = "Oracle JD Edwards (ERP)"

form_fields = [
    {"name": "host", "type": "text", "label": "JDE Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "environment", "type": "text", "label": "Environment", "default": "JDE920"},
    {"name": "role", "type": "text", "label": "Role", "default": "*ALL"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "JD Edwards EnterpriseOne. AIS Server REST services."}
]

def authenticate(form_data):
    """Test Oracle JD Edwards authentication."""
    try:
        import requests
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        environment = form_data.get("environment", "JDE920")
        role = form_data.get("role", "*ALL")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}/jderest"
        
        response = requests.post(
            f"{base_url}/v2/tokenrequest",
            json={
                "username": username,
                "password": password,
                "environment": environment,
                "role": role
            },
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("userInfo"):
                return True, "JD Edwards authentication successful"
        
        return False, "Authentication failed"
            
    except Exception as e:
        return False, f"JD Edwards error: {str(e)}"

