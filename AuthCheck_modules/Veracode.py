# Veracode Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Veracode (Security)"

form_fields = [
    {"name": "api_id", "type": "text", "label": "API ID"},
    {"name": "api_key", "type": "password", "label": "API Key"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API credentials from Administration > API Credentials."},
]


def authenticate(form_data):
    """Attempt to authenticate to Veracode."""
    try:
        import requests
        import hmac
        import hashlib
        import time
        import codecs
    except ImportError:
        return False, "Required packages not available"
    
    api_id = form_data.get('api_id', '').strip()
    api_key = form_data.get('api_key', '').strip()
    
    if not api_id:
        return False, "API ID is required"
    if not api_key:
        return False, "API Key is required"
    
    def generate_veracode_hmac_header(host, url, method):
        """Generate Veracode HMAC authorization header."""
        signing_data = f"id={api_id}&host={host}&url={url}&method={method}"
        timestamp = int(time.time() * 1000)
        nonce = codecs.encode(str(timestamp).encode(), 'hex').decode()
        
        key_bytes = codecs.decode(api_key, 'hex')
        data = f"{signing_data}".encode('utf-8')
        
        signature = hmac.new(key_bytes, data, hashlib.sha256).hexdigest()
        
        return f"VERACODE-HMAC-SHA-256 id={api_id},ts={timestamp},nonce={nonce},sig={signature}"
    
    try:
        host = "api.veracode.com"
        url = "/appsec/v1/applications"
        
        headers = {
            'Authorization': generate_veracode_hmac_header(host, url, "GET"),
            'Accept': 'application/json'
        }
        
        response = requests.get(
            f"https://{host}{url}",
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            apps = data.get('_embedded', {}).get('applications', [])
            app_count = len(apps)
            app_names = [a.get('profile', {}).get('name', 'unknown') for a in apps[:5]]
            
            return True, f"Successfully authenticated to Veracode\nApplications: {app_count}\nSample: {', '.join(app_names) if app_names else 'none'}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Veracode error: {e}"

