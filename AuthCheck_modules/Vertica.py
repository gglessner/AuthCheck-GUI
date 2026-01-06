# Vertica Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Vertica (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Vertica Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "5433",
     "port_toggle": "ssl", "tls_port": "5433", "non_tls_port": "5433"},
    {"name": "database", "type": "text", "label": "Database"},
    {"name": "username", "type": "text", "label": "Username", "default": "dbadmin"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 5433 (TLS/non-TLS same). dbadmin / (set during install)."},
]


def authenticate(form_data):
    """Attempt to authenticate to Vertica."""
    try:
        import vertica_python
    except ImportError:
        return False, "vertica-python package not installed. Run: pip install vertica-python"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '5433').strip()
    database = form_data.get('database', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    ssl = form_data.get('ssl', False)
    
    if not host:
        return False, "Vertica Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        conn_info = {
            'host': host,
            'port': int(port),
            'user': username,
            'password': password,
            'ssl': ssl,
            'connection_timeout': 10
        }
        
        if database:
            conn_info['database'] = database
        
        conn = vertica_python.connect(**conn_info)
        cursor = conn.cursor()
        
        # Get version
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        # Get database info
        cursor.execute("SELECT current_database(), current_user()")
        row = cursor.fetchone()
        current_db = row[0]
        current_user = row[1]
        
        # Get node count
        cursor.execute("SELECT COUNT(*) FROM nodes WHERE node_state = 'UP'")
        node_count = cursor.fetchone()[0]
        
        conn.close()
        return True, f"Successfully authenticated to {version}\nDatabase: {current_db}\nUser: {current_user}\nNodes UP: {node_count}"
        
    except Exception as e:
        return False, f"Vertica error: {e}"

