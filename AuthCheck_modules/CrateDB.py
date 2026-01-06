# CrateDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "CrateDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "CrateDB Host"},
    {"name": "port", "type": "text", "label": "HTTP Port", "default": "4200",
     "port_toggle": "use_ssl", "tls_port": "4200", "non_tls_port": "4200"},
    {"name": "username", "type": "text", "label": "Username", "default": "crate"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "HTTP: 4200, PG: 5432 (TLS/non-TLS same). crate / (blank)."},
]


def authenticate(form_data):
    """Attempt to authenticate to CrateDB."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '4200').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "CrateDB Host is required"
    
    try:
        scheme = "https" if use_ssl else "http"
        base_url = f"{scheme}://{host}:{port}"
        
        auth = None
        if username:
            auth = (username, password)
        
        # Execute query to get version
        response = requests.post(
            f"{base_url}/_sql",
            json={'stmt': 'SELECT version()'},
            auth=auth,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            version = data.get('rows', [['']])[0][0]
            
            # Get tables
            tables_resp = requests.post(
                f"{base_url}/_sql",
                json={'stmt': "SELECT table_name FROM information_schema.tables WHERE table_schema = 'doc' LIMIT 10"},
                auth=auth,
                timeout=10
            )
            table_count = 0
            table_names = []
            if tables_resp.status_code == 200:
                tables_data = tables_resp.json()
                rows = tables_data.get('rows', [])
                table_count = len(rows)
                table_names = [r[0] for r in rows[:5]]
            
            # Get cluster info
            cluster_resp = requests.post(
                f"{base_url}/_sql",
                json={'stmt': 'SELECT COUNT(*) FROM sys.nodes'},
                auth=auth,
                timeout=10
            )
            node_count = 0
            if cluster_resp.status_code == 200:
                node_count = cluster_resp.json().get('rows', [[0]])[0][0]
            
            return True, f"Successfully authenticated to CrateDB\nHost: {host}:{port}\nVersion: {version}\nNodes: {node_count}\nTables: {table_count}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"CrateDB error: {e}"

