"""ERPNext authentication module."""

module_description = "ERPNext (ERP)"

form_fields = [
    {"name": "host", "type": "text", "label": "ERPNext Host", "default": ""},
    {"name": "api_key", "type": "text", "label": "API Key", "default": ""},
    {"name": "api_secret", "type": "password", "label": "API Secret", "default": ""},
    {"name": "username", "type": "text", "label": "Username (Alt)", "default": ""},
    {"name": "password", "type": "password", "label": "Password (Alt)", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "ERPNext (Frappe). Default: Administrator. API keys from user settings."}
]

def authenticate(form_data):
    """Test ERPNext authentication."""
    try:
        import requests
        
        host = form_data.get("host", "").rstrip("/")
        api_key = form_data.get("api_key", "")
        api_secret = form_data.get("api_secret", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        if api_key and api_secret:
            headers = {"Authorization": f"token {api_key}:{api_secret}"}
            response = requests.get(
                f"{base_url}/api/method/frappe.auth.get_logged_user",
                headers=headers,
                verify=verify_ssl,
                timeout=30
            )
        else:
            # Session-based login
            session = requests.Session()
            login_response = session.post(
                f"{base_url}/api/method/login",
                data={"usr": username, "pwd": password},
                verify=verify_ssl,
                timeout=30
            )
            
            if login_response.status_code != 200:
                return False, "Login failed"
            
            response = session.get(
                f"{base_url}/api/method/frappe.auth.get_logged_user",
                verify=verify_ssl,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            user = data.get("message", "unknown")
            return True, f"ERPNext authentication successful ({user})"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"ERPNext error: {str(e)}"

