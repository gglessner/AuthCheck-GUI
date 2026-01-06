"""Ceridian Dayforce authentication module."""

module_description = "Ceridian Dayforce (HR)"

form_fields = [
    {"name": "host", "type": "text", "label": "Dayforce Host", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "client_namespace", "type": "text", "label": "Client Namespace", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Dayforce HCM. REST API on /Api/. Client namespace is company code."}
]

def authenticate(form_data):
    """Test Ceridian Dayforce authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        client_namespace = form_data.get("client_namespace", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}"
        
        response = requests.get(
            f"{base_url}/Api/{client_namespace}/V1/Employees",
            auth=HTTPBasicAuth(username, password),
            params={"pageSize": 1},
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Dayforce authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Dayforce error: {str(e)}"

