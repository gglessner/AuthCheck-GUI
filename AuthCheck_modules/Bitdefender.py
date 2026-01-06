"""Bitdefender authentication module."""

module_description = "Bitdefender (EDR)"

form_fields = [
    {"name": "api_key", "type": "password", "label": "API Key", "default": ""},
    {"name": "access_url", "type": "text", "label": "Access URL", "default": ""},
    {"name": "product", "type": "combo", "label": "Product", "options": ["GravityZone Cloud", "GravityZone On-prem"], "default": "GravityZone Cloud"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Bitdefender GravityZone. API key from Configuration > API Keys."}
]

def authenticate(form_data):
    """Test Bitdefender authentication."""
    try:
        import requests
        import base64
        
        api_key = form_data.get("api_key", "")
        access_url = form_data.get("access_url", "")
        product = form_data.get("product", "GravityZone Cloud")
        
        if not access_url:
            access_url = "https://cloud.gravityzone.bitdefender.com/api"
        
        # API key needs to be base64 encoded
        auth_header = base64.b64encode(f"{api_key}:".encode()).decode()
        
        response = requests.post(
            f"{access_url}/v1.0/jsonrpc/general",
            json={
                "jsonrpc": "2.0",
                "method": "getApiKeyDetails",
                "id": "1"
            },
            headers={
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("result"):
                return True, f"Bitdefender {product} authentication successful"
            elif data.get("error"):
                return False, f"API error: {data['error'].get('message', 'Unknown')}"
        elif response.status_code == 401:
            return False, "Authentication failed"
        
        return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Bitdefender error: {str(e)}"

