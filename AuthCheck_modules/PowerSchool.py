"""PowerSchool SIS authentication module."""

module_description = "PowerSchool (LMS)"

form_fields = [
    {"name": "host", "type": "text", "label": "PowerSchool Host", "default": ""},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "PowerSchool SIS. Plugin credentials from System > Plugin Management."}
]

def authenticate(form_data):
    """Test PowerSchool authentication."""
    try:
        import requests
        import base64
        
        host = form_data.get("host", "").rstrip("/")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        # Base64 encode credentials
        credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        
        response = requests.post(
            f"{base_url}/oauth/access_token",
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={"grant_type": "client_credentials"},
            timeout=30
        )
        
        if response.status_code == 200 and response.json().get("access_token"):
            return True, "PowerSchool authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"PowerSchool error: {str(e)}"

