"""Cerner EHR authentication module."""

module_description = "Cerner (Healthcare)"

form_fields = [
    {"name": "base_url", "type": "text", "label": "Cerner FHIR URL", "default": "https://fhir-open.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d"},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["OAuth2 Client Credentials", "SMART on FHIR", "Open Access"], "default": "Open Access"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Cerner uses OAuth2/SMART. Test sandbox available at code.cerner.com"}
]

def authenticate(form_data):
    """Test Cerner authentication."""
    try:
        import requests
        
        base_url = form_data.get("base_url", "").rstrip("/")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        auth_type = form_data.get("auth_type", "Open Access")
        verify_ssl = form_data.get("verify_ssl", True)
        
        if auth_type == "OAuth2 Client Credentials" and client_id:
            # Get SMART configuration
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
                    "client_secret": client_secret,
                    "scope": "system/*.read"
                },
                verify=verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                return True, "Cerner OAuth2 authentication successful"
            return False, f"Auth failed: {response.text}"
        else:
            # Test open endpoint
            response = requests.get(
                f"{base_url}/metadata",
                verify=verify_ssl,
                timeout=30
            )
            if response.status_code == 200:
                return True, "Cerner FHIR server accessible"
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Cerner error: {str(e)}"

