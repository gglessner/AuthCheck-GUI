"""Geotab fleet management authentication module."""

module_description = "Geotab (Fleet)"

form_fields = [
    {"name": "database", "type": "text", "label": "Database", "default": ""},
    {"name": "username", "type": "text", "label": "Username/Email", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "server", "type": "text", "label": "Server (optional)", "default": "my.geotab.com"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Geotab MyGeotab. Database is the company name in the URL."}
]

def authenticate(form_data):
    """Test Geotab authentication."""
    try:
        import requests
        
        database = form_data.get("database", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        server = form_data.get("server", "my.geotab.com")
        
        response = requests.post(
            f"https://{server}/apiv1",
            json={
                "method": "Authenticate",
                "params": {
                    "database": database,
                    "userName": username,
                    "password": password
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("result", {}).get("credentials"):
                return True, "Geotab authentication successful"
            elif data.get("error"):
                return False, f"Geotab: {data['error'].get('message', 'Unknown error')}"
        
        return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Geotab error: {str(e)}"

