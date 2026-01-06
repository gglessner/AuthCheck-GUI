# MarkLogic Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "MarkLogic (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "MarkLogic Host"},
    {"name": "port", "type": "text", "label": "Admin Port", "default": "8001"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password", "default": "admin"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: admin/admin. Admin port 8001, App Services 8000."},
]


def authenticate(form_data):
    """Attempt to authenticate to MarkLogic."""
    try:
        import requests
        from requests.auth import HTTPDigestAuth
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8001').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "MarkLogic Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        base_url = f"http://{host}:{port}"
        auth = HTTPDigestAuth(username, password)
        
        # Get server version
        response = requests.get(
            f"{base_url}/manage/v2",
            auth=auth,
            headers={'Accept': 'application/json'},
            verify=verify_ssl,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Get cluster info
            cluster_resp = requests.get(
                f"{base_url}/manage/v2/hosts",
                auth=auth,
                headers={'Accept': 'application/json'},
                verify=verify_ssl,
                timeout=10
            )
            host_count = 0
            if cluster_resp.status_code == 200:
                hosts_data = cluster_resp.json()
                host_count = len(hosts_data.get('host-default-list', {}).get('list-items', {}).get('list-item', []))
            
            # Get databases
            db_resp = requests.get(
                f"{base_url}/manage/v2/databases",
                auth=auth,
                headers={'Accept': 'application/json'},
                verify=verify_ssl,
                timeout=10
            )
            db_count = 0
            db_names = []
            if db_resp.status_code == 200:
                db_data = db_resp.json()
                db_items = db_data.get('database-default-list', {}).get('list-items', {}).get('list-item', [])
                db_count = len(db_items)
                db_names = [d.get('nameref', 'unknown') for d in db_items[:5]]
            
            return True, f"Successfully authenticated to MarkLogic\nHost: {host}:{port}\nCluster Hosts: {host_count}\nDatabases: {db_count}\nSample: {', '.join(db_names) if db_names else 'none'}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"MarkLogic error: {e}"

