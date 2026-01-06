"""Blackboard Learn authentication module."""

module_description = "Blackboard Learn (LMS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Blackboard Host", "default": ""},
    {"name": "application_key", "type": "text", "label": "Application Key", "default": ""},
    {"name": "secret", "type": "password", "label": "Secret", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Blackboard Learn. REST API. Register app at developer.blackboard.com."}
]

def authenticate(form_data):
    """Test Blackboard authentication."""
    try:
        import requests
        
        host = form_data.get("host", "").rstrip("/")
        application_key = form_data.get("application_key", "")
        secret = form_data.get("secret", "")
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        # Get OAuth token
        response = requests.post(
            f"{base_url}/learn/api/public/v1/oauth2/token",
            data={"grant_type": "client_credentials"},
            auth=(application_key, secret),
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Blackboard authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Blackboard error: {str(e)}"

