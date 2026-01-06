# QuestDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "QuestDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "QuestDB Host"},
    {"name": "port", "type": "text", "label": "HTTP Port", "default": "9000"},
    {"name": "pg_port", "type": "text", "label": "PostgreSQL Port", "default": "8812"},
    {"name": "username", "type": "text", "label": "Username", "default": "admin"},
    {"name": "password", "type": "password", "label": "Password", "default": "quest"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Default: admin/quest. HTTP 9000, PG wire 8812. Time-series database."},
]


def authenticate(form_data):
    """Attempt to authenticate to QuestDB."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '9000').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    
    if not host:
        return False, "QuestDB Host is required"
    
    try:
        base_url = f"http://{host}:{port}"
        
        auth = None
        if username:
            auth = (username, password)
        
        # Execute simple query to test connection
        response = requests.get(
            f"{base_url}/exec",
            params={'query': 'SELECT version()'},
            auth=auth,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            version = 'unknown'
            if data.get('dataset'):
                version = data['dataset'][0][0] if data['dataset'][0] else 'unknown'
            
            # Get tables
            tables_resp = requests.get(
                f"{base_url}/exec",
                params={'query': 'SHOW TABLES'},
                auth=auth,
                timeout=10
            )
            table_count = 0
            table_names = []
            if tables_resp.status_code == 200:
                tables_data = tables_resp.json()
                if tables_data.get('dataset'):
                    table_count = len(tables_data['dataset'])
                    table_names = [t[0] for t in tables_data['dataset'][:5]]
            
            return True, f"Successfully authenticated to QuestDB\nHost: {host}:{port}\nVersion: {version}\nTables: {table_count}\nSample: {', '.join(table_names) if table_names else 'none'}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"QuestDB error: {e}"

