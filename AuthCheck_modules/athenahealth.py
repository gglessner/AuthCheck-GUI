"""athenahealth API authentication module."""

module_description = "athenahealth (Healthcare)"

form_fields = [
    {"name": "base_url", "type": "text", "label": "API Base URL", "default": "https://api.athenahealth.com"},
    {"name": "version", "type": "combo", "label": "API Version", "options": ["preview1", "v1"], "default": "preview1"},
    {"name": "practice_id", "type": "text", "label": "Practice ID", "default": ""},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Uses OAuth2 client credentials. Register at developer.athenahealth.com"}
]

def authenticate(form_data):
    """Test athenahealth API authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        base_url = form_data.get("base_url", "").rstrip("/")
        version = form_data.get("version", "preview1")
        practice_id = form_data.get("practice_id", "")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        
        # Get access token
        token_response = requests.post(
            f"{base_url}/oauth2/{version}/token",
            data={"grant_type": "client_credentials", "scope": "athena/service/Athenanet.MDP.*"},
            auth=HTTPBasicAuth(client_id, client_secret),
            timeout=30
        )
        
        if token_response.status_code != 200:
            return False, f"Token request failed: {token_response.text}"
        
        access_token = token_response.json().get("access_token")
        
        # Test API access
        if practice_id:
            response = requests.get(
                f"{base_url}/{version}/{practice_id}/ping",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=30
            )
            
            if response.status_code == 200:
                return True, f"athenahealth authentication successful (Practice: {practice_id})"
        
        return True, "athenahealth OAuth2 authentication successful"
            
    except Exception as e:
        return False, f"athenahealth error: {str(e)}"

