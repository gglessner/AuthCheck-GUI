# PlanetScale Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "PlanetScale (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "PlanetScale Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "3306"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "database", "type": "text", "label": "Database"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "MySQL-compatible. Get credentials from branch connection strings."},
]


def authenticate(form_data):
    """Attempt to authenticate to PlanetScale."""
    try:
        import mysql.connector
    except ImportError:
        return False, "mysql-connector-python package not installed. Run: pip install mysql-connector-python"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '3306').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    database = form_data.get('database', '').strip()
    
    if not host:
        return False, "PlanetScale Host is required"
    if not username:
        return False, "Username is required"
    if not database:
        return False, "Database is required"
    
    try:
        conn = mysql.connector.connect(
            host=host,
            port=int(port),
            user=username,
            password=password,
            database=database,
            ssl_disabled=False,  # PlanetScale requires SSL
            connection_timeout=10
        )
        
        cursor = conn.cursor()
        
        # Get version
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        
        # Get tables
        cursor.execute("SHOW TABLES")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get database size
        cursor.execute(f"""
            SELECT SUM(data_length + index_length) / 1024 / 1024 AS size_mb
            FROM information_schema.tables
            WHERE table_schema = '{database}'
        """)
        size_mb = cursor.fetchone()[0] or 0
        
        cursor.close()
        conn.close()
        
        return True, f"Successfully authenticated to PlanetScale\nHost: {host}\nDatabase: {database}\nVersion: {version}\nTables: {len(tables)}\nSize: {size_mb:.2f} MB"
        
    except mysql.connector.Error as e:
        return False, f"PlanetScale error: {e.msg}"
    except Exception as e:
        return False, f"PlanetScale error: {e}"

