"""Shopify authentication module."""

module_description = "Shopify (E-commerce)"

form_fields = [
    {"name": "shop", "type": "text", "label": "Shop Name", "default": ""},
    {"name": "access_token", "type": "password", "label": "Access Token", "default": ""},
    {"name": "api_key", "type": "text", "label": "API Key (Private App)", "default": ""},
    {"name": "api_password", "type": "password", "label": "API Password", "default": ""},
    {"name": "api_version", "type": "text", "label": "API Version", "default": "2024-01"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Shopify Admin API. Access token from app, or API key/password for private apps."}
]

def authenticate(form_data):
    """Test Shopify authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        shop = form_data.get("shop", "")
        access_token = form_data.get("access_token", "")
        api_key = form_data.get("api_key", "")
        api_password = form_data.get("api_password", "")
        api_version = form_data.get("api_version", "2024-01")
        
        base_url = f"https://{shop}.myshopify.com/admin/api/{api_version}"
        
        if access_token:
            headers = {"X-Shopify-Access-Token": access_token}
            auth = None
        else:
            headers = {}
            auth = HTTPBasicAuth(api_key, api_password)
        
        response = requests.get(
            f"{base_url}/shop.json",
            headers=headers,
            auth=auth,
            timeout=30
        )
        
        if response.status_code == 200:
            shop_data = response.json()
            return True, f"Shopify authentication successful ({shop_data.get('shop', {}).get('name', shop)})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Shopify error: {str(e)}"

