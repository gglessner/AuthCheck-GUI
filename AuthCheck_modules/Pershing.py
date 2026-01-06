"""Pershing (BNY Mellon) clearing authentication module."""

module_description = "Pershing (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "Pershing Host", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "firm_id", "type": "text", "label": "Firm ID", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Pershing (BNY Mellon). NetX360 platform. Clearing and custody."}
]

def authenticate(form_data):
    """Test Pershing authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "").rstrip("/")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        firm_id = form_data.get("firm_id", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        headers = {}
        if firm_id:
            headers["X-Firm-ID"] = firm_id
        
        response = requests.get(
            f"{base_url}/api/v1/status",
            auth=HTTPBasicAuth(username, password),
            headers=headers,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Pershing authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Pershing error: {str(e)}"

