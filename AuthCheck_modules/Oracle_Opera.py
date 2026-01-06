"""Oracle Opera PMS authentication module."""

module_description = "Oracle Opera (Travel)"

form_fields = [
    {"name": "host", "type": "text", "label": "Opera Host", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "client_id", "type": "text", "label": "Client ID (OHIP)", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Opera Cloud", "Opera PMS (On-prem)"], "default": "Opera Cloud"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Oracle Opera. OHIP API for cloud. Default: SUPERVISOR."}
]

def authenticate(form_data):
    """Test Oracle Opera authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        product = form_data.get("product", "Opera Cloud")
        verify_ssl = form_data.get("verify_ssl", True)
        
        if product == "Opera Cloud":
            # OAuth2 for OHIP
            token_response = requests.post(
                "https://oauth-us.hospitality.oraclecloud.com/v1/tokens",
                data={
                    "grant_type": "client_credentials",
                    "scope": "read"
                },
                auth=(client_id, client_secret),
                timeout=30
            )
            
            if token_response.status_code == 200:
                return True, "Oracle Opera Cloud authentication successful"
            else:
                return False, f"Token error: HTTP {token_response.status_code}"
        else:
            base_url = f"https://{host}:{port}"
            response = requests.get(
                f"{base_url}/ows_ws/Info.wsp",
                auth=HTTPBasicAuth(username, password),
                verify=verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                return True, "Oracle Opera PMS authentication successful"
            elif response.status_code == 401:
                return False, "Authentication failed"
            else:
                return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Opera error: {str(e)}"

