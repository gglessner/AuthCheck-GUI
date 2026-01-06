"""Sophos authentication module."""

module_description = "Sophos (EDR)"

form_fields = [
    {"name": "client_id", "type": "text", "label": "Client ID", "default": ""},
    {"name": "client_secret", "type": "password", "label": "Client Secret", "default": ""},
    {"name": "tenant_id", "type": "text", "label": "Tenant ID", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["Central", "XG Firewall", "UTM"], "default": "Central"},
    {"name": "host", "type": "text", "label": "Host (On-prem)", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Sophos Central. API credentials from Global Settings > API Credentials."}
]

def authenticate(form_data):
    """Test Sophos authentication."""
    try:
        import requests
        
        client_id = form_data.get("client_id", "")
        client_secret = form_data.get("client_secret", "")
        tenant_id = form_data.get("tenant_id", "")
        product = form_data.get("product", "Central")
        
        if product == "Central":
            # Get access token
            token_response = requests.post(
                "https://id.sophos.com/api/v2/oauth2/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "scope": "token"
                },
                timeout=30
            )
            
            if token_response.status_code != 200:
                return False, f"Token error: {token_response.text}"
            
            access_token = token_response.json().get("access_token")
            
            # Get tenant info
            response = requests.get(
                "https://api.central.sophos.com/whoami/v1",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-Tenant-ID": tenant_id
                },
                timeout=30
            )
        else:
            host = form_data.get("host", "")
            response = requests.get(
                f"https://{host}:4444/api/status",
                auth=(client_id, client_secret),
                timeout=30,
                verify=False
            )
        
        if response.status_code == 200:
            return True, f"Sophos {product} authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Sophos error: {str(e)}"
