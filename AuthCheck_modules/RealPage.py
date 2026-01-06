"""RealPage property management authentication module."""

module_description = "RealPage (Property)"

form_fields = [
    {"name": "host", "type": "text", "label": "RealPage Host", "default": ""},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "pmc_id", "type": "text", "label": "PMC ID", "default": ""},
    {"name": "site_id", "type": "text", "label": "Site ID", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "RealPage OneSite/ILM. API credentials from RealPage support."}
]

def authenticate(form_data):
    """Test RealPage authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "").rstrip("/")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        pmc_id = form_data.get("pmc_id", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        response = requests.get(
            f"{base_url}/api/v1/properties",
            auth=HTTPBasicAuth(username, password),
            params={"pmcid": pmc_id} if pmc_id else {},
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "RealPage authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"RealPage error: {str(e)}"

