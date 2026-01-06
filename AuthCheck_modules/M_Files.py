"""M-Files authentication module."""

module_description = "M-Files (Document)"

form_fields = [
    {"name": "host", "type": "text", "label": "M-Files Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "vault_guid", "type": "text", "label": "Vault GUID", "default": ""},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["M-Files", "Windows"], "default": "M-Files"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "M-Files. Default admin varies by installation."}
]

def authenticate(form_data):
    """Test M-Files authentication."""
    try:
        import requests
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        vault_guid = form_data.get("vault_guid", "")
        auth_type = form_data.get("auth_type", "M-Files")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}/REST"
        
        auth_payload = {
            "Username": username,
            "Password": password,
            "VaultGuid": vault_guid
        }
        
        if auth_type == "Windows":
            auth_payload["WindowsUser"] = True
        
        response = requests.post(
            f"{base_url}/server/authenticationtokens",
            json=auth_payload,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("Value"):
                return True, "M-Files authentication successful"
        elif response.status_code == 401 or response.status_code == 403:
            return False, "Authentication failed"
        
        return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"M-Files error: {str(e)}"

