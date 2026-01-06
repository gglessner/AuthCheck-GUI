"""Duck Creek insurance platform authentication module."""

module_description = "Duck Creek (Insurance)"

form_fields = [
    {"name": "host", "type": "text", "label": "Duck Creek Host", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "client_id", "type": "text", "label": "Client ID (OAuth)", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Policy", "Billing", "Claims", "OnDemand"], "default": "Policy"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Duck Creek Technologies. Policy, Billing, Claims platforms."}
]

def authenticate(form_data):
    """Test Duck Creek authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "").rstrip("/")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        product = form_data.get("product", "Policy")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        if client_id:
            response = requests.post(
                f"{base_url}/identity/connect/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scope": "dcod.api"
                },
                verify=verify_ssl,
                timeout=30
            )
        else:
            response = requests.get(
                f"{base_url}/api/health",
                auth=HTTPBasicAuth(username, password),
                verify=verify_ssl,
                timeout=30
            )
        
        if response.status_code == 200:
            return True, f"Duck Creek {product} authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Duck Creek error: {str(e)}"

