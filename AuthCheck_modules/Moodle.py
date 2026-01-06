"""Moodle LMS authentication module."""

module_description = "Moodle (LMS)"

form_fields = [
    {"name": "host", "type": "text", "label": "Moodle Host", "default": ""},
    {"name": "token", "type": "password", "label": "Web Service Token", "default": ""},
    {"name": "username", "type": "text", "label": "Username (Alt)", "default": ""},
    {"name": "password", "type": "password", "label": "Password (Alt)", "default": ""},
    {"name": "service", "type": "text", "label": "Service Name", "default": "moodle_mobile_app"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Moodle. Token from Site Admin > Plugins > Web services. Default: admin."}
]

def authenticate(form_data):
    """Test Moodle authentication."""
    try:
        import requests
        
        host = form_data.get("host", "").rstrip("/")
        token = form_data.get("token", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        service = form_data.get("service", "moodle_mobile_app")
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        if token:
            response = requests.get(
                f"{base_url}/webservice/rest/server.php",
                params={
                    "wstoken": token,
                    "wsfunction": "core_webservice_get_site_info",
                    "moodlewsrestformat": "json"
                },
                timeout=30
            )
        else:
            # Get token via login
            response = requests.get(
                f"{base_url}/login/token.php",
                params={
                    "username": username,
                    "password": password,
                    "service": service
                },
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("token") or data.get("sitename"):
                return True, "Moodle authentication successful"
            elif data.get("error"):
                return False, f"Moodle: {data.get('error')}"
        
        return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Moodle error: {str(e)}"

