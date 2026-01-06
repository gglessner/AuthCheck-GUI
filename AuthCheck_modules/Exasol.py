# Exasol Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Exasol (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Exasol Host"},
    {"name": "port", "type": "text", "label": "Port", "default": "8563",
     "port_toggle": "use_ssl", "tls_port": "8563", "non_tls_port": "8563"},
    {"name": "use_ssl", "type": "checkbox", "label": "Use SSL"},
    {"name": "username", "type": "text", "label": "Username", "default": "sys"},
    {"name": "password", "type": "password", "label": "Password", "default": "exasol"},
    {"name": "schema", "type": "text", "label": "Schema"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 8563 (TLS/non-TLS same). sys / exasol."},
]


def authenticate(form_data):
    """Attempt to authenticate to Exasol."""
    try:
        import pyexasol
    except ImportError:
        return False, "pyexasol package not installed. Run: pip install pyexasol"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '8563').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    schema = form_data.get('schema', '').strip()
    
    if not host:
        return False, "Exasol Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        conn_args = {
            'dsn': f'{host}:{port}',
            'user': username,
            'password': password
        }
        
        if schema:
            conn_args['schema'] = schema
        
        conn = pyexasol.connect(**conn_args)
        
        # Get version
        stmt = conn.execute("SELECT PARAM_VALUE FROM EXA_METADATA WHERE PARAM_NAME = 'databaseProductVersion'")
        version = stmt.fetchone()[0]
        
        # Get schemas
        stmt = conn.execute("SELECT SCHEMA_NAME FROM EXA_SCHEMAS")
        schemas = [row[0] for row in stmt.fetchall()]
        
        # Get node count
        stmt = conn.execute("SELECT COUNT(*) FROM EXA_SYSTEM_EVENTS WHERE EVENT_TYPE = 'STARTUP'")
        
        conn.close()
        
        return True, f"Successfully authenticated to Exasol\nHost: {host}:{port}\nVersion: {version}\nSchemas: {len(schemas)}\nSample: {', '.join(schemas[:5]) if schemas else 'none'}"
        
    except Exception as e:
        return False, f"Exasol error: {e}"

