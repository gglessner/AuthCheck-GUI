"""BambooHR authentication module."""

module_description = "BambooHR (HR)"

form_fields = [
    {"name": "subdomain", "type": "text", "label": "Subdomain", "default": ""},
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "BambooHR. API key from Account > API Keys. Subdomain from your URL."}
]

def authenticate(form_data):
    """Test BambooHR authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        subdomain = form_data.get("subdomain", "")
        api_key = form_data.get("api_key", "")
        
        base_url = f"https://api.bamboohr.com/api/gateway.php/{subdomain}/v1"
        
        # BambooHR uses API key as username, 'x' as password
        response = requests.get(
            f"{base_url}/employees/directory",
            auth=HTTPBasicAuth(api_key, "x"),
            headers={"Accept": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "BambooHR authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed - invalid API key"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"BambooHR error: {str(e)}"

