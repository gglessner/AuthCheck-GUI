# F5 BIG-IP Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "F5 BIG-IP (Security)"

form_fields = [
    {"name": "host", "type": "text", "label": "BIG-IP Host"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "admin / admin (default). root / default. Port 443 for management."},
]


def authenticate(form_data):
    """Attempt to authenticate to F5 BIG-IP."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "BIG-IP Host is required"
    if not username:
        return False, "Username is required"
    
    if not host.startswith('http'):
        host = f"https://{host}"
    host = host.rstrip('/')
    
    try:
        session = requests.Session()
        session.verify = verify_ssl
        session.auth = (username, password)
        
        headers = {'Content-Type': 'application/json'}
        
        # Get device info
        response = session.get(f"{host}/mgmt/tm/sys/global-settings",
                              headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Get version info
            version_resp = session.get(f"{host}/mgmt/tm/sys/version",
                                       headers=headers, timeout=10)
            version = 'unknown'
            if version_resp.status_code == 200:
                version_data = version_resp.json()
                entries = version_data.get('entries', {})
                for key, val in entries.items():
                    nested = val.get('nestedStats', {}).get('entries', {})
                    version = nested.get('Version', {}).get('description', 'unknown')
                    break
            
            # Get virtual server count
            vs_resp = session.get(f"{host}/mgmt/tm/ltm/virtual",
                                 headers=headers, timeout=10)
            vs_count = 0
            if vs_resp.status_code == 200:
                vs_count = len(vs_resp.json().get('items', []))
            
            # Get pool count
            pool_resp = session.get(f"{host}/mgmt/tm/ltm/pool",
                                   headers=headers, timeout=10)
            pool_count = 0
            if pool_resp.status_code == 200:
                pool_count = len(pool_resp.json().get('items', []))
            
            return True, f"Successfully authenticated to F5 BIG-IP {version}\nUser: {username}\nVirtual Servers: {vs_count}\nPools: {pool_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"F5 BIG-IP error: {e}"

