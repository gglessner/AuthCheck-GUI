"""Verizon Connect fleet management authentication module."""

module_description = "Verizon Connect (Fleet)"

form_fields = [
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "application_id", "type": "text", "label": "Application ID", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Verizon Connect (Fleetmatics/Reveal). API credentials from portal."}
]

def authenticate(form_data):
    """Test Verizon Connect authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        application_id = form_data.get("application_id", "")
        
        response = requests.get(
            "https://fim.api.fleetmatics.com/token",
            auth=HTTPBasicAuth(username, password),
            headers={"X-ApplicationId": application_id} if application_id else {},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Verizon Connect authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Verizon Connect error: {str(e)}"

