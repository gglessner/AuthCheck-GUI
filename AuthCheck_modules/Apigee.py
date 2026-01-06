"""Apigee API Gateway authentication module."""

module_description = "Apigee (Middleware)"

form_fields = [
    {"name": "org", "type": "text", "label": "Organization", "default": ""},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["OAuth2", "Basic Auth", "API Key"], "default": "OAuth2"},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "management_url", "type": "text", "label": "Management API URL", "default": "https://api.enterprise.apigee.com/v1"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Apigee Edge or Apigee X. OAuth2 recommended for Apigee X."}
]

def authenticate(form_data):
    """Test Apigee authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        org = form_data.get("org", "")
        auth_type = form_data.get("auth_type", "OAuth2")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        management_url = form_data.get("management_url", "").rstrip("/")
        
        if auth_type == "OAuth2":
            # Get OAuth token
            token_response = requests.post(
                "https://login.apigee.com/oauth/token",
                data={
                    "grant_type": "password",
                    "username": username,
                    "password": password
                },
                auth=HTTPBasicAuth(client_id, client_secret),
                timeout=30
            )
            
            if token_response.status_code != 200:
                return False, f"OAuth token failed: {token_response.text}"
            
            token = token_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            auth = None
        else:
            headers = {}
            auth = HTTPBasicAuth(username, password)
        
        response = requests.get(
            f"{management_url}/organizations/{org}",
            headers=headers,
            auth=auth,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"Apigee authentication successful for org: {org}"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, f"Apigee error: {str(e)}"
