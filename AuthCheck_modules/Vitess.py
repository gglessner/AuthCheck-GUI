# Vitess Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Vitess (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "VTGate Host"},
    {"name": "port", "type": "text", "label": "MySQL Port", "default": "15306"},
    {"name": "grpc_port", "type": "text", "label": "gRPC Port", "default": "15991"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "database", "type": "text", "label": "Keyspace/Database"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "VTGate MySQL port 15306. MySQL-compatible sharding. CNCF project."},
]


def authenticate(form_data):
    """Attempt to authenticate to Vitess."""
    try:
        import mysql.connector
    except ImportError:
        return False, "mysql-connector-python package not installed. Run: pip install mysql-connector-python"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '15306').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    database = form_data.get('database', '').strip()
    
    if not host:
        return False, "VTGate Host is required"
    
    try:
        conn_params = {
            'host': host,
            'port': int(port),
            'connection_timeout': 10
        }
        
        if username:
            conn_params['user'] = username
            conn_params['password'] = password
        
        if database:
            conn_params['database'] = database
        
        conn = mysql.connector.connect(**conn_params)
        cursor = conn.cursor()
        
        # Get version
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        
        # Get keyspaces
        cursor.execute("SHOW VITESS_KEYSPACES")
        keyspaces = [row[0] for row in cursor.fetchall()]
        
        # Get tablets info
        cursor.execute("SHOW VITESS_TABLETS")
        tablets = cursor.fetchall()
        tablet_count = len(tablets)
        
        cursor.close()
        conn.close()
        
        return True, f"Successfully authenticated to Vitess\nHost: {host}:{port}\nVersion: {version}\nKeyspaces: {len(keyspaces)}\nTablets: {tablet_count}\nSample: {', '.join(keyspaces[:5]) if keyspaces else 'none'}"
        
    except mysql.connector.Error as e:
        return False, f"Vitess error: {e.msg}"
    except Exception as e:
        return False, f"Vitess error: {e}"

