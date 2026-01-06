"""SAP SuccessFactors authentication module."""

module_description = "SAP SuccessFactors (HR)"

form_fields = [
    {"name": "api_url", "type": "text", "label": "API URL", "default": "https://api.successfactors.com"},
    {"name": "company_id", "type": "text", "label": "Company ID", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "client_id", "type": "text", "label": "OAuth Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "OAuth Client Secret", "default": ""},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["Basic", "OAuth2"], "default": "Basic"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "SuccessFactors. Username format: username@companyId. Data centers vary."}
]

def authenticate(form_data):
    """Test SAP SuccessFactors authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        api_url = form_data.get("api_url", "").rstrip("/")
        company_id = form_data.get("company_id", "")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        auth_type = form_data.get("auth_type", "Basic")
        
        if auth_type == "OAuth2" and client_id:
            # OAuth2 flow
            token_response = requests.post(
                f"{api_url}/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "company_id": company_id
                },
                timeout=30
            )
            
            if token_response.status_code == 200:
                return True, "SuccessFactors OAuth2 authentication successful"
            return False, f"OAuth failed: {token_response.text}"
        else:
            # Basic auth
            full_username = f"{username}@{company_id}" if company_id and "@" not in username else username
            
            response = requests.get(
                f"{api_url}/odata/v2/User",
                auth=HTTPBasicAuth(full_username, password),
                params={"$top": 1},
                timeout=30
            )
            
            if response.status_code == 200:
                return True, "SuccessFactors authentication successful"
            elif response.status_code == 401:
                return False, "Authentication failed"
            else:
                return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"SuccessFactors error: {str(e)}"

