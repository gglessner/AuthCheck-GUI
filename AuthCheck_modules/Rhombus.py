"""Rhombus authentication module."""

module_description = "Rhombus (Video)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Rhombus Systems. API key from Console > Integrations."}
]

def authenticate(form_data):
    """Test Rhombus authentication."""
    try:
        import requests
        
        api_key = form_data.get("api_key", "")
        
        response = requests.get(
            "https://api2.rhombussystems.com/api/camera/getMinimalCameraStateList",
            headers={
                "x-auth-scheme": "api-token",
                "x-auth-apikey": api_key
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Rhombus authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Rhombus error: {str(e)}"

