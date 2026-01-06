"""Canvas LMS authentication module."""

module_description = "Canvas LMS (LMS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Canvas Host", "default": ""},
    {"name": "access_token", "type": "password", "label": "Access Token", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Canvas by Instructure. Token from Account > Settings > New Access Token."}
]

def authenticate(form_data):
    """Test Canvas LMS authentication."""
    try:
        import requests
        
        host = form_data.get("host", "").rstrip("/")
        access_token = form_data.get("access_token", "")
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        response = requests.get(
            f"{base_url}/api/v1/users/self",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30
        )
        
        if response.status_code == 200:
            user = response.json()
            return True, f"Canvas authentication successful ({user.get('name', 'unknown')})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Canvas error: {str(e)}"

