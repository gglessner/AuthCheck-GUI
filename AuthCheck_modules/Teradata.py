# Teradata Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Teradata (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Teradata Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "1025",
     "port_toggle": "encryptdata", "tls_port": "1025", "non_tls_port": "1025"},
    {"name": "username", "type": "text", "label": "Username", "default": "dbc"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "database", "type": "text", "label": "Database"},
    {"name": "logmech", "type": "combo", "label": "Login Mechanism", "options": ["TD2", "LDAP", "KRB5", "TDNEGO"], "default": "TD2"},
    {"name": "encryptdata", "type": "checkbox", "label": "Encrypt Data"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 1025 (TLS/non-TLS same). dbc / dbc. TD2=native."},
]


def authenticate(form_data):
    """Attempt to authenticate to Teradata."""
    try:
        import teradatasql
    except ImportError:
        return False, "teradatasql package not installed. Run: pip install teradatasql"
    
    host = form_data.get('host', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    database = form_data.get('database', '').strip()
    logmech = form_data.get('logmech', 'TD2')
    encryptdata = form_data.get('encryptdata', False)
    
    if not host:
        return False, "Teradata Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        conn_params = {
            'host': host,
            'user': username,
            'password': password,
            'logmech': logmech,
            'encryptdata': 'true' if encryptdata else 'false'
        }
        
        if database:
            conn_params['database'] = database
        
        conn = teradatasql.connect(**conn_params)
        cursor = conn.cursor()
        
        # Get version
        cursor.execute("SELECT InfoData FROM DBC.DBCInfoV WHERE InfoKey = 'VERSION'")
        version = cursor.fetchone()[0]
        
        # Get database count
        cursor.execute("SELECT COUNT(*) FROM DBC.DatabasesV WHERE DBKind = 'D'")
        db_count = cursor.fetchone()[0]
        
        # Get current user
        cursor.execute("SELECT USER")
        current_user = cursor.fetchone()[0]
        
        conn.close()
        return True, f"Successfully authenticated to Teradata {version}\nUser: {current_user}\nDatabases: {db_count}"
        
    except Exception as e:
        return False, f"Teradata error: {e}"

