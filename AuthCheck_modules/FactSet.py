"""FactSet authentication module."""

module_description = "FactSet (Financial)"

form_fields = [
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["api", "api-sandbox"], "default": "api-sandbox"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "FactSet Developer Portal. Username-Serial format."}
]

def authenticate(form_data):
    """Test FactSet authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        username = form_data.get("username", "")
        api_key = form_data.get("api_key", "")
        environment = form_data.get("environment", "api-sandbox")
        
        base_url = f"https://{environment}.factset.com"
        
        response = requests.get(
            f"{base_url}/analytics/engines/v3/calculations",
            auth=HTTPBasicAuth(username, api_key),
            timeout=30
        )
        
        if response.status_code in [200, 404]:  # 404 means auth worked, no calculations
            return True, "FactSet authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"FactSet error: {str(e)}"

