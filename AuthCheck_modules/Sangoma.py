# Sangoma PBX Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Sangoma PBX (PBX)"

form_fields = [
    {"name": "host", "type": "text", "label": "Sangoma Host"},
    {"name": "port", "type": "text", "label": "HTTPS Port", "default": "443"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: admin/admin. Web interface. Also includes FreePBX."},
]


def authenticate(form_data):
    """Attempt to authenticate to Sangoma PBX."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '443').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Sangoma Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        base_url = f"https://{host}:{port}"
        session = requests.Session()
        session.verify = verify_ssl
        
        # Try REST API authentication
        auth_url = f"{base_url}/admin/api/api/token"
        
        response = session.post(
            auth_url,
            json={'username': username, 'password': password},
            timeout=15
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            
            if access_token:
                headers = {'Authorization': f'Bearer {access_token}'}
                
                # Get system info
                sys_resp = session.get(
                    f"{base_url}/admin/api/api/system/info",
                    headers=headers,
                    timeout=10
                )
                
                version = 'unknown'
                if sys_resp.status_code == 200:
                    sys_data = sys_resp.json()
                    version = sys_data.get('version', 'unknown')
                
                return True, f"Successfully authenticated to Sangoma PBX\nHost: {host}:{port}\nVersion: {version}\nAPI Access: Granted"
            else:
                return True, f"Successfully authenticated to Sangoma PBX\nHost: {host}:{port}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            # Try web login
            login_resp = session.post(
                f"{base_url}/admin/config.php",
                data={'username': username, 'password': password},
                timeout=15,
                allow_redirects=True
            )
            
            if 'logout' in login_resp.text.lower():
                return True, f"Successfully authenticated to Sangoma PBX\nHost: {host}:{port}\nWeb Access: Granted"
            else:
                return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Sangoma error: {e}"

