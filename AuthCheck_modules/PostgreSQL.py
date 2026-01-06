# PostgreSQL Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "PostgreSQL (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "5432",
     "port_toggle": "ssl_mode", "tls_port": "5432", "non_tls_port": "5432"},
    {"name": "database", "type": "text", "label": "Database", "default": "postgres"},
    {"name": "username", "type": "text", "label": "Username", "default": "postgres"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "ssl_mode", "type": "combo", "label": "SSL Mode",
     "options": ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]},
    {"name": "ssl_cert", "type": "file", "label": "Client Certificate", "filter": "Certificate Files (*.crt *.pem);;All Files (*)"},
    {"name": "ssl_key", "type": "file", "label": "Client Key", "filter": "Key Files (*.key *.pem);;All Files (*)"},
    {"name": "ssl_rootcert", "type": "file", "label": "Root CA Certificate", "filter": "Certificate Files (*.crt *.pem);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 5432 (TLS/non-TLS same). postgres / postgres, admin / admin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to PostgreSQL.
    
    Args:
        form_data (dict): Form field values
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        import psycopg2
    except ImportError:
        try:
            import psycopg
            psycopg2 = psycopg
        except ImportError:
            return False, "psycopg2 or psycopg package not installed. Run: pip install psycopg2-binary"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    database = form_data.get('database', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    ssl_mode = form_data.get('ssl_mode', 'prefer')
    ssl_cert = form_data.get('ssl_cert', '').strip()
    ssl_key = form_data.get('ssl_key', '').strip()
    ssl_rootcert = form_data.get('ssl_rootcert', '').strip()
    
    if not host:
        return False, "Host is required"
    if not database:
        return False, "Database is required"
    if not username:
        return False, "Username is required"
    
    try:
        conn_params = {
            'host': host,
            'port': int(port) if port else 5432,
            'dbname': database,
            'user': username,
            'password': password,
            'sslmode': ssl_mode,
            'connect_timeout': 10,
        }
        
        if ssl_cert:
            conn_params['sslcert'] = ssl_cert
        if ssl_key:
            conn_params['sslkey'] = ssl_key
        if ssl_rootcert:
            conn_params['sslrootcert'] = ssl_rootcert
        
        conn = psycopg2.connect(**conn_params)
        
        # Get server version
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        cursor.execute("SELECT current_database(), current_user")
        db_name, current_user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return True, f"Successfully authenticated to PostgreSQL\nDatabase: {db_name}\nUser: {current_user}\nVersion: {version}"
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        if "password authentication failed" in error_msg.lower():
            return False, "Authentication failed: Invalid username or password"
        elif "could not connect" in error_msg.lower():
            return False, f"Connection failed: Could not connect to {host}:{port}"
        elif "does not exist" in error_msg.lower():
            return False, f"Database '{database}' does not exist"
        else:
            return False, f"PostgreSQL error: {e}"
    except Exception as e:
        return False, f"Error: {e}"

