"""Travelport GDS authentication module."""

module_description = "Travelport (Travel)"

form_fields = [
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "pcc", "type": "text", "label": "PCC/Branch", "default": ""},
    {"name": "target_branch", "type": "text", "label": "Target Branch", "default": ""},
    {"name": "environment", "type": "combo", "label": "Environment", "options": ["preproduction", "production"], "default": "preproduction"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Travelport (Galileo/Apollo/Worldspan). UAPI credentials."}
]

def authenticate(form_data):
    """Test Travelport authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        pcc = form_data.get("pcc", "")
        environment = form_data.get("environment", "preproduction")
        
        if environment == "preproduction":
            base_url = "https://emea.universal-api.pp.travelport.com"
        else:
            base_url = "https://emea.universal-api.travelport.com"
        
        # UAPI uses SOAP - simplified ping check
        response = requests.get(
            f"{base_url}/B2BGateway/connect/uAPI/SystemService",
            auth=HTTPBasicAuth(f"Universal API/{username}", password),
            timeout=30
        )
        
        if response.status_code in [200, 405]:  # 405 = endpoint exists but wrong method
            return True, f"Travelport authentication successful ({environment})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Travelport error: {str(e)}"

