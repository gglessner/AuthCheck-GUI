"""Verifone payment terminal authentication module."""

module_description = "Verifone (ATM)"

form_fields = [
    {"name": "host", "type": "text", "label": "Terminal Host/IP", "default": ""},
    {"name": "port", "type": "text", "label": "Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": ""},
    {"name": "password", "type": "password", "label": "Password", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Engage Hub", "PayWare", "VHQ", "VX Terminal", "MX Terminal"], "default": "Engage Hub"},
    {"name": "api_key", "type": "password", "label": "API Key (Cloud)", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Verifone. Engage Hub cloud management. VHQ for on-prem. Terminal: 1 Z A P (supervisor)."}
]

def authenticate(form_data):
    """Test Verifone authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        host = form_data.get("host", "")
        port = form_data.get("port", "443")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        product = form_data.get("product", "Engage Hub")
        api_key = form_data.get("api_key", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        if product == "Engage Hub":
            # Cloud-based management
            if api_key:
                response = requests.get(
                    "https://api.verifone.cloud/v1/devices",
                    headers={"Authorization": f"Bearer {api_key}"},
                    params={"limit": 1},
                    timeout=30
                )
            else:
                response = requests.post(
                    "https://api.verifone.cloud/v1/auth/token",
                    json={"username": username, "password": password},
                    timeout=30
                )
        elif product == "VHQ":
            base_url = f"https://{host}:{port}"
            response = requests.get(
                f"{base_url}/vhq/api/v1/status",
                auth=HTTPBasicAuth(username, password),
                verify=verify_ssl,
                timeout=30
            )
        else:
            # Direct terminal access
            base_url = f"https://{host}:{port}"
            response = requests.get(
                f"{base_url}/api/status",
                auth=HTTPBasicAuth(username, password),
                verify=verify_ssl,
                timeout=30
            )
        
        if response.status_code == 200:
            return True, f"Verifone {product} authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Verifone error: {str(e)}"

