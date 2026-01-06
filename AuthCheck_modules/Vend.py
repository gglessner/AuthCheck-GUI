"""Vend/Lightspeed X-Series authentication module."""

module_description = "Vend / Lightspeed X-Series (POS)"

form_fields = [
    {"name": "domain", "type": "text", "label": "Domain Prefix", "default": ""},
    {"name": "access_token", "type": "password", "label": "Personal Token", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Vend (now Lightspeed X-Series). Personal token from Setup > Personal Tokens."}
]

def authenticate(form_data):
    """Test Vend authentication."""
    try:
        import requests
        
        domain = form_data.get("domain", "")
        access_token = form_data.get("access_token", "")
        
        base_url = f"https://{domain}.vendhq.com/api/2.0"
        
        response = requests.get(
            f"{base_url}/outlets",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Vend authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Vend error: {str(e)}"

