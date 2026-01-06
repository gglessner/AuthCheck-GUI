"""HL7 FHIR authentication module."""

module_description = "HL7 FHIR (Healthcare)"

form_fields = [
    {"name": "base_url", "type": "text", "label": "FHIR Server URL", "default": "https://localhost/fhir"},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["Basic", "Bearer Token", "OAuth2", "SMART on FHIR"], "default": "Basic"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password/Token", "default": ""},
    {"name": "client_id", "type": "text", "label": "OAuth Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "OAuth Client Secret", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "SMART on FHIR uses OAuth2. Common test servers use Basic auth."}
]

def authenticate(form_data):
    """Test FHIR server authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        base_url = form_data.get("base_url", "").rstrip("/")
        auth_type = form_data.get("auth_type", "Basic")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        headers = {"Accept": "application/fhir+json"}
        auth = None
        
        if auth_type == "Basic" and username:
            auth = HTTPBasicAuth(username, password)
        elif auth_type == "Bearer Token" and password:
            headers["Authorization"] = f"Bearer {password}"
        
        # Try metadata endpoint
        response = requests.get(
            f"{base_url}/metadata",
            auth=auth,
            headers=headers,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, f"FHIR server authentication successful"
        else:
            return False, f"FHIR error: HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"FHIR error: {str(e)}"

