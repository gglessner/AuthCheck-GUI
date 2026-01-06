"""Jamf Pro authentication module."""

module_description = "Jamf Pro (MDM)"

form_fields = [
    {"name": "host", "type": "text", "label": "Jamf Pro URL", "default": "yourorg.jamfcloud.com"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "client_id", "type": "text", "label": "Client ID (API)", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Jamf Pro. Classic API uses Basic auth. Jamf Pro API uses OAuth2."}
]

def authenticate(form_data):
    """Test Jamf Pro authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}"
        
        if client_id and client_secret:
            # OAuth2 flow
            token_response = requests.post(
                f"{base_url}/api/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret
                },
                verify=verify_ssl,
                timeout=30
            )
            
            if token_response.status_code == 200:
                return True, "Jamf Pro OAuth2 authentication successful"
            else:
                return False, f"OAuth failed: {token_response.text}"
        else:
            # Classic API with Basic auth
            response = requests.get(
                f"{base_url}/JSSResource/activationcode",
                auth=HTTPBasicAuth(username, password),
                headers={"Accept": "application/json"},
                verify=verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                return True, "Jamf Pro Classic API authentication successful"
            elif response.status_code == 401:
                return False, "Authentication failed"
            else:
                return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Jamf error: {str(e)}"

