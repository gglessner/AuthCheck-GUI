"""Mimecast authentication module."""

module_description = "Mimecast (Email Security)"

form_fields = [
    {"name": "base_url", "type": "text", "label": "API Base URL", "default": "https://us-api.mimecast.com"},
    {"name": "app_id", "type": "text", "label": "Application ID", "default": ""},
    {"name": "app_key", "type": "password", "label": "Application Key", "default": ""},
    {"name": "access_key", "type": "text", "label": "Access Key", "default": ""},
    {"name": "secret_key", "type": "password", "label": "Secret Key", "default": ""},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API credentials from Administration > Services > API and Platform Integrations."}
]

def authenticate(form_data):
    """Test Mimecast authentication."""
    try:
        import requests
        import base64
        import uuid
        import hashlib
        import hmac
        from datetime import datetime
        
        base_url = form_data.get("base_url", "https://us-api.mimecast.com")
        app_id = form_data.get("app_id", "")
        app_key = form_data.get("app_key", "")
        access_key = form_data.get("access_key", "")
        secret_key = form_data.get("secret_key", "")
        
        uri = "/api/account/get-account"
        request_id = str(uuid.uuid4())
        
        # Create auth header
        hdr_date = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S UTC")
        data_to_sign = f"{hdr_date}:{request_id}:{uri}:{app_key}"
        
        secret_key_bytes = base64.b64decode(secret_key)
        signature = base64.b64encode(
            hmac.new(secret_key_bytes, data_to_sign.encode(), hashlib.sha1).digest()
        ).decode()
        
        headers = {
            "Authorization": f"MC {access_key}:{signature}",
            "x-mc-app-id": app_id,
            "x-mc-date": hdr_date,
            "x-mc-req-id": request_id,
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{base_url}{uri}",
            headers=headers,
            json={"data": []},
            timeout=30
        )
        
        if response.status_code == 200:
            return True, "Mimecast authentication successful"
        elif response.status_code == 401:
            return False, "Authentication failed"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        return False, f"Mimecast error: {str(e)}"

