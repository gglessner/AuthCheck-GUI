# Duo Security Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Duo Security (IAM)"

form_fields = [
    {"name": "host", "type": "text", "label": "API Hostname"},
    {"name": "integration_key", "type": "text", "label": "Integration Key"},
    {"name": "secret_key", "type": "password", "label": "Secret Key"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "API Hostname: api-xxx.duosecurity.com. From Admin Panel > Applications > Admin API."},
]


def authenticate(form_data):
    """Attempt to authenticate to Duo Security Admin API."""
    try:
        import requests
        import hmac
        import hashlib
        import base64
        import email.utils
        import urllib.parse
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    integration_key = form_data.get('integration_key', '').strip()
    secret_key = form_data.get('secret_key', '')
    
    if not host:
        return False, "API Hostname is required"
    if not integration_key:
        return False, "Integration Key is required"
    if not secret_key:
        return False, "Secret Key is required"
    
    try:
        # Build Duo signed request
        method = "GET"
        path = "/admin/v1/info/authentication_attempts"
        params = ""
        
        now = email.utils.formatdate()
        
        canon = [now, method.upper(), host.lower(), path, params]
        canon_str = "\n".join(canon)
        
        sig = hmac.new(
            secret_key.encode('utf-8'),
            canon_str.encode('utf-8'),
            hashlib.sha1
        ).hexdigest()
        
        auth = f"{integration_key}:{sig}"
        auth_b64 = base64.b64encode(auth.encode('utf-8')).decode('utf-8')
        
        headers = {
            'Date': now,
            'Authorization': f'Basic {auth_b64}'
        }
        
        response = requests.get(f"https://{host}{path}",
                               headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Get user count
            users_resp = requests.get(f"https://{host}/admin/v1/users",
                                     headers=headers, timeout=10)
            user_count = 0
            if users_resp.status_code == 200:
                users_data = users_resp.json()
                if 'response' in users_data:
                    user_count = len(users_data['response'])
            
            return True, f"Successfully authenticated to Duo Security\nAPI Host: {host}\nUsers: {user_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 403:
            return False, "Authentication failed: API access denied"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"Duo Security error: {e}"

