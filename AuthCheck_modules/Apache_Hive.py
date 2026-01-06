# Apache Hive Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Apache Hive (BigData)"

form_fields = [
    {"name": "host", "type": "text", "label": "HiveServer2 Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "10000",
     "port_toggle": "use_ssl", "tls_port": "10001", "non_tls_port": "10000"},
    {"name": "database", "type": "text", "label": "Database", "default": "default"},
    {"name": "auth_type", "type": "combo", "label": "Authentication",
     "options": ["NONE", "LDAP", "KERBEROS", "CUSTOM"]},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "use_ssl", "type": "checkbox", "label": "Enable SSL"},
    {"name": "kerberos_service_name", "type": "text", "label": "Kerberos Service Name", "default": "hive"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 10001, Non-TLS: 10000. NONE: any user. LDAP: hive / hive"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to Apache Hive via HiveServer2.
    """
    try:
        from pyhive import hive
    except ImportError:
        return False, "pyhive package not installed. Run: pip install pyhive[hive]"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    database = form_data.get('database', 'default').strip()
    auth_type = form_data.get('auth_type', 'NONE')
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    kerberos_service_name = form_data.get('kerberos_service_name', 'hive').strip()
    
    if not host:
        return False, "HiveServer2 Host is required"
    
    try:
        port_num = int(port) if port else 10000
        
        conn_kwargs = {
            'host': host,
            'port': port_num,
            'database': database,
        }
        
        if auth_type == "NONE":
            conn_kwargs['auth'] = 'NONE'
            if username:
                conn_kwargs['username'] = username
        elif auth_type == "LDAP":
            conn_kwargs['auth'] = 'LDAP'
            conn_kwargs['username'] = username
            conn_kwargs['password'] = password
        elif auth_type == "KERBEROS":
            conn_kwargs['auth'] = 'KERBEROS'
            conn_kwargs['kerberos_service_name'] = kerberos_service_name
        elif auth_type == "CUSTOM":
            conn_kwargs['auth'] = 'CUSTOM'
            conn_kwargs['username'] = username
            conn_kwargs['password'] = password
        
        connection = hive.connect(**conn_kwargs)
        cursor = connection.cursor()
        
        # Execute a simple query
        cursor.execute("SELECT current_database()")
        result = cursor.fetchone()
        current_db = result[0] if result else database
        
        cursor.close()
        connection.close()
        
        return True, f"Successfully authenticated to Hive at {host}:{port_num}\nDatabase: {current_db}"
        
    except Exception as e:
        error_msg = str(e)
        if "AuthorizationException" in error_msg or "Authentication" in error_msg:
            return False, f"Authentication failed: {e}"
        return False, f"Hive error: {e}"

