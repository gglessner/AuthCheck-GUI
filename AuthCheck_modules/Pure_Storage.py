# Pure Storage FlashArray Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Pure Storage FlashArray (Storage)"

form_fields = [
    {"name": "host", "type": "text", "label": "Array Host"},
    {"name": "username", "type": "text", "label": "Username", "default": "pureuser"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "api_token", "type": "password", "label": "API Token (Alternative)"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "pureuser / pureuser (default). API token from Settings > Users."},
]


def authenticate(form_data):
    """Attempt to authenticate to Pure Storage FlashArray."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    api_token = form_data.get('api_token', '').strip()
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "Array Host is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        
        headers = {'Content-Type': 'application/json'}
        
        if api_token:
            # Use API token
            auth_data = {'api_token': api_token}
        else:
            if not username:
                return False, "Username or API Token is required"
            auth_data = {'username': username, 'password': password}
        
        # Authenticate and get session
        auth_resp = session.post(f"{host}/api/2.0/login", 
                                json=auth_data, headers=headers, timeout=10)
        
        if auth_resp.status_code in [200, 201]:
            # Get array info
            array_resp = session.get(f"{host}/api/2.0/arrays", headers=headers, timeout=10)
            
            if array_resp.status_code == 200:
                array_data = array_resp.json()
                items = array_data.get('items', [])
                
                if items:
                    array_name = items[0].get('name', 'unknown')
                    version = items[0].get('version', 'unknown')
                else:
                    array_name = 'unknown'
                    version = 'unknown'
                
                # Get volume count
                vol_resp = session.get(f"{host}/api/2.0/volumes", headers=headers, timeout=10)
                vol_count = 0
                if vol_resp.status_code == 200:
                    vol_count = vol_resp.json().get('total_item_count', 0)
                
                # Get capacity
                space_resp = session.get(f"{host}/api/2.0/arrays/space", headers=headers, timeout=10)
                capacity_info = ""
                if space_resp.status_code == 200:
                    space_data = space_resp.json().get('items', [{}])[0]
                    capacity = space_data.get('capacity', 0)
                    used = space_data.get('space', {}).get('total_physical', 0)
                    if capacity > 0:
                        used_pct = (used / capacity) * 100
                        capacity_info = f"\nCapacity: {used_pct:.1f}% used"
                
                # Logout
                session.post(f"{host}/api/2.0/logout", headers=headers, timeout=5)
                
                return True, f"Successfully authenticated to Pure Storage\nArray: {array_name}\nPurity: {version}\nVolumes: {vol_count}{capacity_info}"
            else:
                return True, f"Successfully authenticated to Pure Storage at {host}"
        elif auth_resp.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {auth_resp.status_code}: {auth_resp.text[:200]}"
            
    except Exception as e:
        return False, f"Pure Storage error: {e}"

