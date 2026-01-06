# TiDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "TiDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "TiDB Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "4000",
     "port_toggle": "use_ssl", "tls_port": "4000", "non_tls_port": "4000"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "database", "type": "text", "label": "Database"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 4000 (TLS/non-TLS same). root / (blank). MySQL-compatible."},
]


def authenticate(form_data):
    """Attempt to authenticate to TiDB."""
    try:
        import mysql.connector
    except ImportError:
        return False, "mysql-connector-python package not installed. Run: pip install mysql-connector-python"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '4000').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    database = form_data.get('database', '').strip()
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "TiDB Host is required"
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
        
        # Get TiDB version
        cursor.execute("SELECT tidb_version()")
        tidb_version = cursor.fetchone()[0]
        
        # Get database list
        cursor.execute("SHOW DATABASES")
        databases = [row[0] for row in cursor.fetchall()]
        
        # Get cluster info
        cursor.execute("SELECT TYPE, INSTANCE, STATUS_ADDRESS FROM INFORMATION_SCHEMA.CLUSTER_INFO LIMIT 10")
        cluster_nodes = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        node_summary = {}
        for node_type, instance, status in cluster_nodes:
            node_summary[node_type] = node_summary.get(node_type, 0) + 1
        
        cluster_info = ", ".join([f"{k}: {v}" for k, v in node_summary.items()])
        
        return True, f"Successfully authenticated to TiDB\nHost: {host}:{port}\nVersion: {tidb_version[:80]}\nDatabases: {len(databases)}\nCluster: {cluster_info}"
        
    except mysql.connector.Error as e:
        return False, f"TiDB error: {e.msg}"
    except Exception as e:
        return False, f"TiDB error: {e}"

