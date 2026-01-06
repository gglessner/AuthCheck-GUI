# Apache Impala Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Impala (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "Impala Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "21050",
     "port_toggle": "use_ssl", "tls_port": "21050", "non_tls_port": "21050"},
    {"name": "database", "type": "text", "label": "Database", "default": "default"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["NOSASL", "PLAIN", "GSSAPI", "LDAP"]},
    {"name": "use_ssl", "type": "checkbox", "label": "Enable SSL"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "kerberos_service_name", "type": "text", "label": "Kerberos Service Name", "default": "impala"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 21050 (TLS/non-TLS same). Default: no auth. LDAP/Kerberos."},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Impala.
    """
    try:
        from impala.dbapi import connect
    except ImportError:
        return False, "impyla package not installed. Run: pip install impyla"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    database = form_data.get('database', 'default').strip()
    auth_type = form_data.get('auth_type', 'NOSASL')
    use_ssl = form_data.get('use_ssl', False)
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    kerberos_service_name = form_data.get('kerberos_service_name', 'impala').strip()
    
    if not host:
        return False, "Impala Host is required"
    
    try:
        port_num = int(port) if port else 21050
        
        conn_kwargs = {
            'host': host,
            'port': port_num,
            'database': database,
            'timeout': 10,
        }
        
        if auth_type == "NOSASL":
            conn_kwargs['auth_mechanism'] = 'NOSASL'
        elif auth_type == "PLAIN":
            conn_kwargs['auth_mechanism'] = 'PLAIN'
            conn_kwargs['user'] = username
            conn_kwargs['password'] = password
        elif auth_type == "LDAP":
            conn_kwargs['auth_mechanism'] = 'LDAP'
            conn_kwargs['user'] = username
            conn_kwargs['password'] = password
        elif auth_type == "GSSAPI":
            conn_kwargs['auth_mechanism'] = 'GSSAPI'
            conn_kwargs['kerberos_service_name'] = kerberos_service_name
        
        if use_ssl:
            conn_kwargs['use_ssl'] = True
        
        conn = connect(**conn_kwargs)
        cursor = conn.cursor()
        
        # Get version
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        
        # Get current database
        cursor.execute("SELECT current_database()")
        current_db = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return True, f"Successfully authenticated to Apache Impala\nDatabase: {current_db}\nVersion: {version}"
        
    except Exception as e:
        error_msg = str(e)
        if "Authentication" in error_msg or "SASL" in error_msg:
            return False, f"Authentication failed: {e}"
        return False, f"Impala error: {e}"

