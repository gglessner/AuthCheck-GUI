"""Allscripts EHR authentication module."""

module_description = "Allscripts (Healthcare)"

form_fields = [
    {"name": "base_url", "type": "text", "label": "API Base URL", "default": "https://api.allscripts.com"},
    {"name": "app_name", "type": "text", "label": "Application Name", "default": ""},
    {"name": "app_username", "type": "text", "label": "App Username", "default": ""},
    {"name": "app_password", "type": "password", "label": "App Password", "default": ""},
    {"name": "svc_username", "type": "text", "label": "Service Username", "default": ""},
    {"name": "svc_password", "type": "password", "label": "Service Password", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Unity API. Requires registered app credentials and service account."}
]

def authenticate(form_data):
    """Test Allscripts authentication."""
    try:
        import requests
        
        base_url = form_data.get("base_url", "").rstrip("/")
        app_name = form_data.get("app_name", "")
        app_username = form_data.get("app_username", "")
        app_password = form_data.get("app_password", "")
        svc_username = form_data.get("svc_username", "")
        svc_password = form_data.get("svc_password", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        # Unity API authentication
        response = requests.post(
            f"{base_url}/Unity/UnityService.svc/json/GetToken",
            json={
                "appname": app_name,
                "appusername": app_username,
                "apppassword": app_password,
                "svcusername": svc_username,
                "svcpassword": svc_password
            },
            headers={"Content-Type": "application/json"},
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result and not result.get("Error"):
                return True, "Allscripts authentication successful"
            else:
                return False, f"Auth failed: {result.get('Error', 'Unknown error')}"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Allscripts error: {str(e)}"

