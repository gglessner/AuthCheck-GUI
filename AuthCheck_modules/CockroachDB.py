# CockroachDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "CockroachDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "26257"},
    {"name": "database", "type": "text", "label": "Database", "default": "defaultdb"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "ssl_mode", "type": "combo", "label": "SSL Mode", "options": ["disable", "require", "verify-ca", "verify-full"], "default": "require"},
    {"name": "ssl_cert", "type": "file", "label": "SSL Certificate", "filter": "Certificates (*.crt *.pem);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "root / (no password in insecure mode). Port 26257. CockroachDB Cloud uses SSL."},
]


def authenticate(form_data):
    """Attempt to authenticate to CockroachDB."""
    try:
        import psycopg2
    except ImportError:
        return False, "psycopg2 package not installed. Run: pip install psycopg2-binary"
    
    host = form_data.get('host', 'localhost').strip()
    port = form_data.get('port', '26257').strip()
    database = form_data.get('database', 'defaultdb').strip()
    username = form_data.get('username', 'root').strip()
    password = form_data.get('password', '')
    ssl_mode = form_data.get('ssl_mode', 'require')
    ssl_cert = form_data.get('ssl_cert', '').strip()
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        conn_params = {
            'host': host,
            'port': int(port),
            'database': database,
            'user': username,
            'password': password,
            'sslmode': ssl_mode,
            'connect_timeout': 10
        }
        
        if ssl_cert:
            conn_params['sslrootcert'] = ssl_cert
        
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Get version
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        # Verify it's CockroachDB
        if 'CockroachDB' not in version:
            conn.close()
            return False, "Connected to PostgreSQL, but not CockroachDB"
        
        # Get cluster info
        cursor.execute("SELECT node_id, address FROM crdb_internal.gossip_nodes LIMIT 5")
        nodes = cursor.fetchall()
        
        # Get database count
        cursor.execute("SELECT COUNT(*) FROM information_schema.schemata")
        db_count = cursor.fetchone()[0]
        
        conn.close()
        
        crdb_version = version.split('CockroachDB')[1].split()[0] if 'CockroachDB' in version else 'unknown'
        return True, f"Successfully authenticated to CockroachDB {crdb_version}\nNodes: {len(nodes)}\nDatabases: {db_count}"
        
    except Exception as e:
        return False, f"CockroachDB error: {e}"

