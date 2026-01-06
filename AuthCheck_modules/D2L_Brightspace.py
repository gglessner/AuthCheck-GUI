"""D2L Brightspace authentication module."""

module_description = "D2L Brightspace (LMS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Brightspace Host", "default": ""},
    {"name": "app_id", "type": "text", "label": "Application ID", "default": ""},
    {"name": "app_key", "type": "password", "label": "Application Key", "default": ""},
    {"name": "user_id", "type": "text", "label": "User ID", "default": ""},
    {"name": "user_key", "type": "password", "label": "User Key", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "D2L Brightspace. Valence API. App credentials from Brightspace admin."}
]

def authenticate(form_data):
    """Test D2L Brightspace authentication."""
    try:
        import requests
        
        host = form_data.get("host", "").rstrip("/")
        app_id = form_data.get("app_id", "")
        app_key = form_data.get("app_key", "")
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        # D2L uses signed URLs - simplified check
        response = requests.get(
            f"{base_url}/d2l/api/versions/",
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "D2L Brightspace reachable (full auth requires Valence SDK)"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"D2L error: {str(e)}"

