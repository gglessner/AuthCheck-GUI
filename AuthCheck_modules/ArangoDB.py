# ArangoDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "ArangoDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "ArangoDB Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "8529",
     "port_toggle": "use_ssl", "tls_port": "8529", "non_tls_port": "8529"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "database", "type": "text", "label": "Database", "default": "_system"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 8529 (TLS/non-TLS same). root / (blank). Multi-model DB."},
]


def authenticate(form_data):
    """Attempt to authenticate to ArangoDB."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8529').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    database = form_data.get('database', '_system').strip()
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "ArangoDB Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        scheme = "https" if use_ssl else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        # Authenticate
        auth_resp = requests.post(
            f"{base_url}/_open/auth",
            json={'username': username, 'password': password},
            timeout=15
        )
        
        if auth_resp.status_code == 200:
            token = auth_resp.json().get('jwt')
            headers = {'Authorization': f'bearer {token}'}
            
            # Get server version
            version_resp = requests.get(
                f"{base_url}/_api/version",
                headers=headers,
                timeout=10
            )
            version = 'unknown'
            if version_resp.status_code == 200:
                version = version_resp.json().get('version', 'unknown')
            
            # Get databases
            dbs_resp = requests.get(
                f"{base_url}/_api/database",
                headers=headers,
                timeout=10
            )
            db_count = 0
            if dbs_resp.status_code == 200:
                db_count = len(dbs_resp.json().get('result', []))
            
            # Get collections in current database
            colls_resp = requests.get(
                f"{base_url}/_db/{database}/_api/collection",
                headers=headers,
                timeout=10
            )
            coll_count = 0
            if colls_resp.status_code == 200:
                coll_count = len(colls_resp.json().get('result', []))
            
            return True, f"Successfully authenticated to ArangoDB\nHost: {host}:{port}\nVersion: {version}\nDatabases: {db_count}\nCollections ({database}): {coll_count}"
        elif auth_resp.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {auth_resp.status_code}: {auth_resp.text[:200]}"
            
    except Exception as e:
        return False, f"ArangoDB error: {e}"

