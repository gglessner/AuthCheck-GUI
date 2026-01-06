# YugabyteDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "YugabyteDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "YugabyteDB Host"},
    {"name": "port", "type": "text", "label": "YSQL Port", "default": "5433",
     "port_toggle": "use_ssl", "tls_port": "5433", "non_tls_port": "5433"},
    {"name": "username", "type": "text", "label": "Username", "default": "yugabyte"},
    {"name": "password", "type": "password", "label": "Password", "default": "yugabyte"},
    {"name": "database", "type": "text", "label": "Database", "default": "yugabyte"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "YSQL: 5433 (TLS/non-TLS same), YCQL: 9042. yugabyte / yugabyte"},
]


def authenticate(form_data):
    """Attempt to authenticate to YugabyteDB."""
    try:
        import psycopg2
    except ImportError:
        return False, "psycopg2 package not installed. Run: pip install psycopg2-binary"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '5433').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    database = form_data.get('database', 'yugabyte').strip()
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "YugabyteDB Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        conn_params = {
            'host': host,
            'port': int(port),
            'user': username,
            'password': password,
            'dbname': database,
            'connect_timeout': 10
        }
        
        if use_ssl:
            conn_params['sslmode'] = 'require'
        
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Get version
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        # Get database list
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
        databases = [row[0] for row in cursor.fetchall()]
        
        # Get table count
        cursor.execute("""
            SELECT count(*) FROM information_schema.tables 
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        """)
        table_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return True, f"Successfully authenticated to YugabyteDB\nHost: {host}:{port}\nVersion: {version[:60]}...\nDatabases: {len(databases)}\nTables: {table_count}"
        
    except psycopg2.OperationalError as e:
        error_msg = str(e).split('\n')[0]
        return False, f"YugabyteDB error: {error_msg}"
    except Exception as e:
        return False, f"YugabyteDB error: {e}"

