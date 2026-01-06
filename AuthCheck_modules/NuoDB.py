# NuoDB Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "NuoDB (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "NuoDB Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "48004",
     "port_toggle": "use_ssl", "tls_port": "48004", "non_tls_port": "48004"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "username", "type": "text", "label": "Username", "default": "dba"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "database", "type": "text", "label": "Database"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 48004 (TLS/non-TLS same). dba / (configured)."},
]


def authenticate(form_data):
    """Attempt to authenticate to NuoDB."""
    try:
        import pynuodb
    except ImportError:
        return False, "pynuodb package not installed. Run: pip install pynuodb"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '48004').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    database = form_data.get('database', '').strip()
    
    if not host:
        return False, "NuoDB Host is required"
    if not username:
        return False, "Username is required"
    if not database:
        return False, "Database is required"
    
    try:
        conn = pynuodb.connect(
            database=database,
            host=host,
            user=username,
            password=password,
            options={'port': port}
        )
        
        cursor = conn.cursor()
        
        # Get version
        cursor.execute("SELECT GETNUODBVERSION() FROM DUAL")
        version = cursor.fetchone()[0]
        
        # Get tables
        cursor.execute("SELECT TABLENAME FROM SYSTEM.TABLES WHERE SCHEMA = ?", (username.upper(),))
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return True, f"Successfully authenticated to NuoDB\nHost: {host}:{port}\nDatabase: {database}\nVersion: {version}\nTables: {len(tables)}"
        
    except Exception as e:
        return False, f"NuoDB error: {e}"

