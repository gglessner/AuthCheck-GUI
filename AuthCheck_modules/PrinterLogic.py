"""PrinterLogic authentication module."""

module_description = "PrinterLogic (Print)"

form_fields = [
    {"name": "host", "type": "text", "label": "PrinterLogic Host", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "api_key", "type": "password", "label": "API Key (Alt)", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "PrinterLogic. SaaS or on-prem. Default: admin / admin."}
]

def authenticate(form_data):
    """Test PrinterLogic authentication."""
    try:
        import requests
        
        host = form_data.get("host", "").rstrip("/")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        api_key = form_data.get("api_key", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        if api_key:
            response = requests.get(
                f"{base_url}/api/v1/printers",
                headers={"Authorization": f"Bearer {api_key}"},
                params={"limit": 1},
                verify=verify_ssl,
                timeout=30
            )
        else:
            # Session-based login
            session = requests.Session()
            response = session.post(
                f"{base_url}/api/login",
                json={"username": username, "password": password},
                verify=verify_ssl,
                timeout=30
            )
        
        if response.status_code == 200:
            return True, "PrinterLogic authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"PrinterLogic error: {str(e)}"

