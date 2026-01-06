# Apache Phoenix Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Phoenix (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Query Server Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "8765",
     "port_toggle": "use_ssl", "tls_port": "8765", "non_tls_port": "8765"},
    {"name": "database", "type": "text", "label": "Schema/Database"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["None", "SPNEGO", "Basic"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "use_ssl", "type": "checkbox", "label": "Enable SSL"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 8765 (TLS/non-TLS same). Uses HBase auth. Default: no auth"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Phoenix Query Server.
    """
    try:
        import phoenixdb
    except ImportError:
        return False, "phoenixdb package not installed. Run: pip install phoenixdb"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    database = form_data.get('database', '').strip()
    auth_type = form_data.get('auth_type', 'None')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    use_ssl = form_data.get('use_ssl', False)
    
    if not host:
        return False, "Query Server Host is required"
    
    try:
        port_num = port if port else "8765"
        scheme = "https" if use_ssl else "http"
        database_url = f"{scheme}://{host}:{port_num}/"
        
        conn_kwargs = {}
        if auth_type == "Basic" and username:
            conn_kwargs['authentication'] = 'BASIC'
            conn_kwargs['avatica_user'] = username
            conn_kwargs['avatica_password'] = password
        elif auth_type == "SPNEGO":
            conn_kwargs['authentication'] = 'SPNEGO'
        
        conn = phoenixdb.connect(database_url, autocommit=True, **conn_kwargs)
        cursor = conn.cursor()
        
        # Get version
        cursor.execute("SELECT * FROM SYSTEM.CATALOG LIMIT 1")
        
        # List schemas
        cursor.execute("SELECT DISTINCT TABLE_SCHEM FROM SYSTEM.CATALOG WHERE TABLE_SCHEM IS NOT NULL")
        schemas = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return True, f"Successfully connected to Apache Phoenix at {host}:{port_num}\nSchemas: {schemas[:10]}{'...' if len(schemas) > 10 else ''}"
        
    except Exception as e:
        error_msg = str(e)
        if "Authentication" in error_msg or "401" in error_msg:
            return False, f"Authentication failed: {e}"
        return False, f"Phoenix error: {e}"

