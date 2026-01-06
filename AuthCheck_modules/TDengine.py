# TDengine Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "TDengine (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "TDengine Host"},
    {"name": "port", "type": "text", "label": "REST Port", "default": "6041"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password", "default": "taosdata"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: root/taosdata. REST port 6041. Time-series for IoT."},
]


def authenticate(form_data):
    """Attempt to authenticate to TDengine."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '6041').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not host:
        return False, "TDengine Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        base_url = f"http://{host}:{port}"
        auth = (username, password)
        
        # Get server info
        response = requests.get(
            f"{base_url}/rest/login/{username}/{password}",
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'succ':
                # Get databases
                db_resp = requests.post(
                    f"{base_url}/rest/sql",
                    auth=auth,
                    data='SHOW DATABASES',
                    timeout=10
                )
                db_count = 0
                db_names = []
                if db_resp.status_code == 200:
                    db_data = db_resp.json()
                    if db_data.get('data'):
                        db_count = len(db_data['data'])
                        db_names = [d[0] for d in db_data['data'][:5]]
                
                # Get version
                ver_resp = requests.post(
                    f"{base_url}/rest/sql",
                    auth=auth,
                    data='SELECT SERVER_VERSION()',
                    timeout=10
                )
                version = 'unknown'
                if ver_resp.status_code == 200:
                    ver_data = ver_resp.json()
                    if ver_data.get('data'):
                        version = ver_data['data'][0][0]
                
                return True, f"Successfully authenticated to TDengine\nHost: {host}:{port}\nVersion: {version}\nDatabases: {db_count}\nSample: {', '.join(db_names) if db_names else 'none'}"
            else:
                return False, f"Authentication failed: {data.get('desc', 'Unknown error')}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"TDengine error: {e}"

