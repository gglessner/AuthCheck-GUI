"""Loomis SafePoint authentication module."""

module_description = "Loomis SafePoint (ATM)"

form_fields = [
    {"name": "host", "type": "text", "label": "SafePoint Host/IP", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": False},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Loomis SafePoint smart safes. Titan series."}
]

def authenticate(form_data):
    """Test Loomis SafePoint authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", False)
        
        base_url = f"https://{host}:{port}"
        
        response = requests.get(
            f"{base_url}/api/status",
            auth=HTTPBasicAuth(username, password),
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Loomis SafePoint authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Loomis error: {str(e)}"

