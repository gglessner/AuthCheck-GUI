"""BigCommerce authentication module."""

module_description = "BigCommerce (E-commerce)"

form_fields = [
    {"name": "store_hash", "type": "text", "label": "Store Hash", "default": ""},
    {"name": "access_token", "type": "password", "label": "Access Token", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "BigCommerce. API credentials from Store > Advanced Settings > API Accounts."}
]

def authenticate(form_data):
    """Test BigCommerce authentication."""
    try:
        import requests
        
        store_hash = form_data.get("store_hash", "")
        access_token = form_data.get("access_token", "")
        
        response = requests.get(
            f"https://api.bigcommerce.com/stores/{store_hash}/v2/store",
            headers={
                "X-Auth-Token": access_token,
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            store = response.json()
            return True, f"BigCommerce authentication successful ({store.get('name', store_hash)})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"BigCommerce error: {str(e)}"

