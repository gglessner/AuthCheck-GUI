"""OSIsoft PI System authentication module."""

module_description = "OSIsoft PI (ICS)"

form_fields = [
    {"name": "host", "type": "text", "label": "PI Web API Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "auth_type", "type": "combo", "label": "Auth Type", "options": ["Basic", "Kerberos"], "default": "Basic"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "OSIsoft PI (now AVEVA). PI Web API. Windows auth common."}
]

def authenticate(form_data):
    """Test OSIsoft PI authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        from requests_ntlm import HttpNtlmAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        auth_type = form_data.get("auth_type", "Basic")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}/piwebapi"
        
        if auth_type == "Kerberos":
            auth = HttpNtlmAuth(username, password)
        else:
            auth = HTTPBasicAuth(username, password)
        
        response = requests.get(
            f"{base_url}/system",
            auth=auth,
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "OSIsoft PI authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except ImportError:
        # Fallback without NTLM
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}:{port}/piwebapi"
        
        response = requests.get(
            f"{base_url}/system",
            auth=HTTPBasicAuth(username, password),
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "OSIsoft PI authentication successful"
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, f"PI error: {str(e)}"

