"""Verkada authentication module."""

module_description = "Verkada (Video)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "org_id", "type": "text", "label": "Organization ID", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Verkada Command. API key from Admin > Integrations > API."}
]

def authenticate(form_data):
    """Test Verkada authentication."""
    try:
        import requests
        
        api_key = form_data.get("api_key", "")
        org_id = form_data.get("org_id", "")
        
        response = requests.get(
            "https://api.verkada.com/cameras/v1/devices",
            headers={
                "x-api-key": api_key
            },
            params={"org_id": org_id} if org_id else {},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            cam_count = len(data.get("cameras", []))
            return True, f"Verkada authentication successful ({cam_count} cameras)"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Verkada error: {str(e)}"

