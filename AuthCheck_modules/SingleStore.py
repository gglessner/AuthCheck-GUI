# SingleStore (MemSQL) Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "SingleStore / MemSQL (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "SingleStore Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "3306",
     "port_toggle": "use_ssl", "tls_port": "3307", "non_tls_port": "3306"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "database", "type": "text", "label": "Database"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 3307, Non-TLS: 3306. root / (configured). MySQL-compatible."},
]


def authenticate(form_data):
    """Attempt to authenticate to SingleStore."""
    try:
        import mysql.connector
    except ImportError:
        return False, "mysql-connector-python package not installed. Run: pip install mysql-connector-python"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '3306').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    database = form_data.get('database', '').strip()
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "SingleStore Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        conn_params = {
            'host': host,
            'port': int(port),
            'user': username,
            'password': password,
            'connection_timeout': 10
        }
        
        if database:
            conn_params['database'] = database
        
        if use_ssl:
            conn_params['ssl_disabled'] = False
        
        conn = mysql.connector.connect(**conn_params)
        cursor = conn.cursor()
        
        # Get version
        cursor.execute("SELECT @@memsql_version")
        version = cursor.fetchone()[0]
        
        # Get database list
        cursor.execute("SHOW DATABASES")
        databases = [row[0] for row in cursor.fetchall()]
        
        # Get cluster info
        cursor.execute("SHOW AGGREGATORS")
        aggregators = cursor.fetchall()
        
        cursor.execute("SHOW LEAVES")
        leaves = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return True, f"Successfully authenticated to SingleStore\nHost: {host}:{port}\nVersion: {version}\nDatabases: {len(databases)}\nAggregators: {len(aggregators)}, Leaves: {len(leaves)}"
        
    except mysql.connector.Error as e:
        return False, f"SingleStore error: {e.msg}"
    except Exception as e:
        return False, f"SingleStore error: {e}"

