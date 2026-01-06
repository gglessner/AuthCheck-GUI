# VoltDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "VoltDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "VoltDB Host"},
    {"name": "port", "type": "text", "label": "Client Port", "default": "21212"},
    {"name": "http_port", "type": "text", "label": "HTTP Port", "default": "8080",
     "port_toggle": "use_ssl", "tls_port": "8443", "non_tls_port": "8080"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Client: 21212. HTTP: 8080, HTTPS: 8443. In-memory ACID SQL."},
]


def authenticate(form_data):
    """Attempt to authenticate to VoltDB."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '21212').strip()
    http_port = form_data.get('http_port', '8080').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not host:
        return False, "VoltDB Host is required"
    
    try:
        base_url = f"http://{host}:{http_port}"
        
        auth = None
        if username:
            auth = (username, password)
        
        # Get system info via JSON API
        response = requests.get(
            f"{base_url}/api/1.0/",
            params={'Procedure': '@SystemInformation', 'Parameters': '["OVERVIEW"]'},
            auth=auth,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Parse system info
            version = 'unknown'
            cluster_state = 'unknown'
            host_count = 0
            
            if 'results' in data and data['results']:
                results = data['results'][0].get('data', [])
                for row in results:
                    if len(row) >= 2:
                        key, value = row[0], row[1]
                        if key == 'VERSION':
                            version = value
                        elif key == 'CLUSTERSTATE':
                            cluster_state = value
                        elif key == 'HOSTCOUNT':
                            host_count = int(value)
            
            # Get tables
            tables_resp = requests.get(
                f"{base_url}/api/1.0/",
                params={'Procedure': '@SystemCatalog', 'Parameters': '["TABLES"]'},
                auth=auth,
                timeout=10
            )
            table_count = 0
            if tables_resp.status_code == 200:
                tables_data = tables_resp.json()
                if 'results' in tables_data and tables_data['results']:
                    table_count = len(tables_data['results'][0].get('data', []))
            
            return True, f"Successfully authenticated to VoltDB\nHost: {host}:{http_port}\nVersion: {version}\nCluster State: {cluster_state}\nHosts: {host_count}\nTables: {table_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"VoltDB error: {e}"

