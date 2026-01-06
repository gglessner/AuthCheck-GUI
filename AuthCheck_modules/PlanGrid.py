"""PlanGrid (Autodesk Build) authentication module."""

module_description = "PlanGrid (Construction)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "PlanGrid (now Autodesk Build). API key from PlanGrid account settings."}
]

def authenticate(form_data):
    """Test PlanGrid authentication."""
    try:
        import requests
        
        api_key = form_data.get("api_key", "")
        
        response = requests.get(
            "https://io.plangrid.com/me",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30
        )
        
        if response.status_code == 200:
            user = response.json()
            return True, f"PlanGrid authentication successful ({user.get('email', 'unknown')})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"PlanGrid error: {str(e)}"

