"""Tyk API Gateway authentication module."""

module_description = "Tyk (Middleware)"

form_fields = [
    {"name": "gateway_url", "type": "text", "label": "Gateway URL", "default": "http://localhost:8080"},
    {"name": "dashboard_url", "type": "text", "label": "Dashboard URL", "default": "http://localhost:3000"},
    {"name": "api_key", "type": "password", "label": "API Key (x-tyk-authorization)", "default": ""},
    {"name": "admin_secret", "type": "password", "label": "Admin Secret", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Gateway port 8080. Dashboard port 3000. Admin secret in tyk.conf"}
]

def authenticate(form_data):
    """Test Tyk authentication."""
    try:
        import requests
        
        gateway_url = form_data.get("gateway_url", "http://localhost:8080").rstrip("/")
        api_key = form_data.get("api_key", "")
        admin_secret = form_data.get("admin_secret", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        headers = {}
        if api_key:
            headers["x-tyk-authorization"] = api_key
        if admin_secret:
            headers["x-tyk-authorization"] = admin_secret
        
        response = requests.get(
            f"{gateway_url}/tyk/apis",
            headers=headers,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            apis = response.json()
            return True, f"Tyk authentication successful ({len(apis)} APIs)"
        elif response.status_code == 401 or response.status_code == 403:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Tyk error: {str(e)}"

