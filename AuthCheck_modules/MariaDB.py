# MariaDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "MariaDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "3306",
     "port_toggle": "use_ssl", "tls_port": "3306", "non_tls_port": "3306"},
    {"name": "database", "type": "text", "label": "Database"},
    {"name": "username", "type": "text", "label": "Username", "default": "root"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 3306 (TLS/non-TLS same). root / (empty). MySQL-compatible."},
]


def authenticate(form_data):
    """Attempt to authenticate to MariaDB."""
    try:
        import mariadb
    except ImportError:
        try:
            import mysql.connector as mariadb
        except ImportError:
            return False, "mariadb or mysql-connector-python package not installed. Run: pip install mariadb"
    
    host = form_data.get('host', 'localhost').strip()
    port = form_data.get('port', '3306').strip()
    database = form_data.get('database', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        conn_params = {
            'host': host,
            'port': int(port),
            'user': username,
            'password': password,
        }
        
        if database:
            conn_params['database'] = database
        
        if use_ssl:
            conn_params['ssl'] = True
        
        conn = mariadb.connect(**conn_params)
        cursor = conn.cursor()
        
        # Get version
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        
        # Verify it's MariaDB
        is_mariadb = 'mariadb' in version.lower()
        
        # Get database count
        cursor.execute("SELECT COUNT(*) FROM information_schema.SCHEMATA")
        db_count = cursor.fetchone()[0]
        
        # Get current user
        cursor.execute("SELECT CURRENT_USER()")
        current_user = cursor.fetchone()[0]
        
        conn.close()
        
        db_type = "MariaDB" if is_mariadb else "MySQL-compatible"
        return True, f"Successfully authenticated to {db_type}\nVersion: {version}\nUser: {current_user}\nDatabases: {db_count}"
        
    except Exception as e:
        return False, f"MariaDB error: {e}"

