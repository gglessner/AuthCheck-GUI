"""WooCommerce authentication module."""

module_description = "WooCommerce (E-commerce)"

form_fields = [
    {"name": "site_url", "type": "text", "label": "Site URL", "default": ""},
    {"name": "consumer_key", "type": "text", "label": "Consumer Key", "default": ""},
    {"name": "consumer_secret", "type": "password", "label": "Consumer Secret", "default": ""},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL", "default": True},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "WooCommerce REST API. Keys from WP Admin > WooCommerce > Settings > Advanced > REST API."}
]

def authenticate(form_data):
    """Test WooCommerce authentication."""
    try:
        import requests
        from requests.auth import HTTPBasicAuth
        
        site_url = form_data.get("site_url", "").rstrip("/")
        consumer_key = form_data.get("consumer_key", "")
        consumer_secret = form_data.get("consumer_secret", "")
        verify_ssl = form_data.get("verify_ssl", True)
        
        response = requests.get(
            f"{site_url}/wp-json/wc/v3/system_status",
            auth=HTTPBasicAuth(consumer_key, consumer_secret),
            verify=verify_ssl,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            wc_version = data.get("environment", {}).get("version", "unknown")
            return True, f"WooCommerce authentication successful (v{wc_version})"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"WooCommerce error: {str(e)}"

