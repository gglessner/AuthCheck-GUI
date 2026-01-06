"""Thought Machine Vault authentication module."""

module_description = "Thought Machine Vault (Financial)"

form_fields = [
    {"name": "host", "type": "text", "label": "Vault Host", "default": ""},
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Thought Machine Vault. Cloud-native core banking."}
]

def authenticate(form_data):
    """Test Thought Machine Vault authentication."""
    try:
        import requests
        
        host = form_data.get("host", "").rstrip("/")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        response = requests.post(
            f"{base_url}/v1/auth/token",
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            },
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200 and response.json().get("access_token"):
            return True, "Thought Machine Vault authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Thought Machine error: {str(e)}"

