"""Epic EHR authentication module."""

module_description = "Epic (Healthcare)"

form_fields = [
    {"name": "base_url", "type": "text", "label": "Epic FHIR URL", "default": "https://fhir.epic.com/interconnect-fhir-oauth"},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "username", "type": "text", "label": "Username (EMP)", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["Backend OAuth2", "SMART on FHIR", "EMP Credentials"], "default": "Backend OAuth2"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Epic uses OAuth2/SMART on FHIR. Requires registered app."}
]

def authenticate(form_data):
    """Test Epic authentication."""
    try:
        import requests
        
        base_url = form_data.get("base_url", "").rstrip("/")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        auth_type = form_data.get("auth_type", "Backend OAuth2")
        verify_ssl = form_data.get("verify_ssl", True)
        
        if auth_type == "Backend OAuth2":
            # Get token endpoint from SMART configuration
            smart_config = requests.get(
                f"{base_url}/.well-known/smart-configuration",
                verify=verify_ssl,
                timeout=30
            ).json()
            
            token_url = smart_config.get("token_endpoint")
            
            response = requests.post(
                token_url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret
                },
                verify=verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200 and "access_token" in response.json():
                return True, "Epic OAuth2 authentication successful"
            else:
                return False, f"Epic auth failed: {response.text}"
        else:
            # Try metadata endpoint
            response = requests.get(
                f"{base_url}/metadata",
                verify=verify_ssl,
                timeout=30
            )
            if response.status_code == 200:
                return True, "Epic FHIR server accessible"
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Epic error: {str(e)}"

