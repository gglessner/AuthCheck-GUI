"""Magento/Adobe Commerce authentication module."""

module_description = "Magento / Adobe Commerce (E-commerce)"

form_fields = [
    {"name": "host", "type": "text", "label": "Magento Host", "default": ""},
    {"name": "username", "type": "text", "label": "Admin Username", "default": ""},
    {"name": "password", "type": "password", "label": "Admin Password", "default": ""},
    {"name": "integration_token", "type": "password", "label": "Integration Token (Alt)", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Magento 2 / Adobe Commerce. Integration tokens from System > Integrations."}
]

def authenticate(form_data):
    """Test Magento authentication."""
    try:
        import requests
        
        host = form_data.get("host", "").rstrip("/")
        username = form_data.get("username", "")
        password = form_data.get("password", "")
        integration_token = form_data.get("integration_token", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        base_url = f"https://{host}" if not host.startswith("http") else host
        
        if integration_token:
            # Use integration token
            response = requests.get(
                f"{base_url}/rest/V1/store/storeConfigs",
                headers={"Authorization": f"Bearer {integration_token}"},
                verify=verify_ssl,
                timeout=30
            )
        else:
            # Admin token authentication
            token_response = requests.post(
                f"{base_url}/rest/V1/integration/admin/token",
                json={"username": username, "password": password},
                verify=verify_ssl,
                timeout=30
            )
            
            if token_response.status_code != 200:
                return False, "Token request failed"
            
            token = token_response.json()
            
            response = requests.get(
                f"{base_url}/rest/V1/store/storeConfigs",
                headers={"Authorization": f"Bearer {token}"},
                verify=verify_ssl,
                timeout=30
            )
        
        if response.status_code == 200:
            return True, "Magento authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Magento error: {str(e)}"

