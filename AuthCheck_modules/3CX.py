# 3CX Phone System Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "3CX Phone System (PBX)"

form_fields = [
    {"name": "host", "type": "text", "label": "3CX Host"},
    {"name": "port", "type": "text", "label": "HTTPS Port", "default": "5001"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Management console port 5001. Credentials set during install."},
]


def authenticate(form_data):
    """Attempt to authenticate to 3CX Phone System."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '5001').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "3CX Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        base_url = f"https://{host}:{port}"
        session = requests.Session()
        session.verify = verify_ssl
        
        # 3CX uses a management console API
        login_url = f"{base_url}/api/login"
        
        login_data = {
            'Username': username,
            'Password': password
        }
        
        response = session.post(
            login_url,
            json=login_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('Status') == 'Authenticated' or result.get('Success'):
                # Get system status
                status_resp = session.get(
                    f"{base_url}/api/SystemStatus",
                    timeout=10
                )
                
                version = 'unknown'
                extensions = 0
                if status_resp.status_code == 200:
                    status = status_resp.json()
                    version = status.get('Version', 'unknown')
                    extensions = status.get('ExtensionsTotal', 0)
                
                return True, f"Successfully authenticated to 3CX\nHost: {host}:{port}\nVersion: {version}\nExtensions: {extensions}"
            else:
                return False, "Authentication failed: Invalid credentials"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"3CX error: {e}"

