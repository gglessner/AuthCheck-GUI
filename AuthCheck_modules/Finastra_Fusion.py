"""Finastra Fusion authentication module."""

module_description = "Finastra Fusion (Financial)"

form_fields = [
    {"name": "base_url", "type": "text", "label": "Fusion API URL", "default": "https://api.fusionfabric.cloud"},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "tenant_id", "type": "text", "label": "Tenant ID", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "FusionFabric.cloud uses OAuth2. Register at developer.fusionfabric.cloud"}
]

def authenticate(form_data):
    """Test Finastra Fusion authentication."""
    try:
        import requests
        
        base_url = form_data.get("base_url", "").rstrip("/")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        response = requests.post(
            f"{base_url}/login/v1/sandbox/oidc/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            },
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200 and "access_token" in response.json():
            return True, "Finastra Fusion authentication successful"
        else:
            return False, f"Auth failed: {response.text}"
            
    except Exception as e:
        return False, f"Finastra error: {str(e)}"

