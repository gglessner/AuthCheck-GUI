# OrientDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "OrientDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "OrientDB Host"},
    {"name": "port", "type": "text", "label": "HTTP Port", "default": "2480",
     "port_toggle": "use_ssl", "tls_port": "2481", "non_tls_port": "2480"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password", "default": "root"},
    {"name": "database", "type": "text", "label": "Database"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "HTTP: 2480, HTTPS: 2481, Binary: 2424. root / root."},
]


def authenticate(form_data):
    """Attempt to authenticate to OrientDB."""
    try:
        import requests
    except ImportError:
        return False, "requests package not installed"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '2480').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    database = form_data.get('database', '').strip()
    
    if not host:
        return False, "OrientDB Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        base_url = f"http://{host}:{port}"
        auth = (username, password)
        
        # Get server info
        response = requests.get(
            f"{base_url}/server",
            auth=auth,
            timeout=15
        )
        
        if response.status_code == 200:
            server_info = response.json()
            version = server_info.get('version', 'unknown')
            
            # Get databases
            dbs_resp = requests.get(
                f"{base_url}/listDatabases",
                auth=auth,
                timeout=10
            )
            db_names = []
            if dbs_resp.status_code == 200:
                db_data = dbs_resp.json()
                db_names = db_data.get('databases', [])
            
            if database:
                # Connect to specific database
                db_resp = requests.get(
                    f"{base_url}/database/{database}",
                    auth=auth,
                    timeout=10
                )
                if db_resp.status_code == 200:
                    db_info = db_resp.json()
                    classes = db_info.get('classes', [])
                    return True, f"Successfully authenticated to OrientDB\nHost: {host}:{port}\nVersion: {version}\nDatabase: {database}\nClasses: {len(classes)}"
            
            return True, f"Successfully authenticated to OrientDB\nHost: {host}:{port}\nVersion: {version}\nDatabases: {len(db_names)}\nSample: {', '.join(db_names[:5]) if db_names else 'none'}"
        elif response.status_code == 401:
            return False, "Authentication failed: Invalid credentials"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:200]}"
            
    except Exception as e:
        return False, f"OrientDB error: {e}"

