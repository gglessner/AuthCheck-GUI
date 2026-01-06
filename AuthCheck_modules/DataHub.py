"""DataHub authentication module."""

module_description = "DataHub (BigData)"

form_fields = [
    {"name": "gms_url", "type": "text", "label": "GMS URL", "default": "http://localhost:8080"},
    {"name": "frontend_url", "type": "text", "label": "Frontend URL", "default": "http://localhost:9002"},
    {"name": "token", "type": "password", "label": "Access Token", "default": ""},
    {"name": "username", "type": "text", "label": "Username (OIDC)", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: datahub/datahub. GMS port 8080, Frontend port 9002."}
]

def authenticate(form_data):
    """Test DataHub authentication."""
    try:
        import requests
        
        gms_url = form_data.get("gms_url", "http://localhost:8080").rstrip("/")
        token = form_data.get("token", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        # Try GMS health check
        response = requests.get(
            f"{gms_url}/health",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"DataHub GMS authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"DataHub error: {str(e)}"

