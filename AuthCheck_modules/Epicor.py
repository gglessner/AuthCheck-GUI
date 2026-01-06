"""Epicor ERP authentication module."""

module_description = "Epicor (ERP)"

form_fields = [
    {"name": "host", "type": "text", "label": "Epicor Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "company", "type": "text", "label": "Company", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Kinetic", "Prophet 21", "Eclipse"], "default": "Kinetic"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Epicor Kinetic (formerly E10). REST API on /api/v1/."}
]

def authenticate(form_data):
    """Test Epicor authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        company = form_data.get("company", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}"
        
        headers = {}
        if company:
            headers["X-Company"] = company
        
        response = requests.get(
            f"{base_url}/api/v1/Erp.BO.CompanySvc/Companies",
            auth=HTTPBasicAuth(username, password),
            headers=headers,
            params={"$top": 1},
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Epicor authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Epicor error: {str(e)}"

