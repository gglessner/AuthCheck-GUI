# SAP HANA Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "SAP HANA (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "HANA Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "30015",
     "port_toggle": "encrypt", "tls_port": "30015", "non_tls_port": "30015"},
    {"name": "username", "type": "text", "label": "Username", "default": "SYSTEM"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "encrypt", "type": "checkbox", "label": "Use SSL/TLS"},
    {"name": "verify_ssl", "type": "checkbox", "label": "Verify SSL Certificate"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 3NN15 (TLS/non-TLS same). SYSTEM / (set during install)."},
]


def authenticate(form_data):
    """Attempt to authenticate to SAP HANA."""
    try:
        from hdbcli import dbapi
    except ImportError:
        return False, "hdbcli package not installed. Run: pip install hdbcli"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '30015').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    encrypt = form_data.get('encrypt', False)
    verify_ssl = form_data.get('verify_ssl', False)
    
    if not host:
        return False, "HANA Host is required"
    if not username:
        return False, "Username is required"
    
    try:
        conn = dbapi.connect(
            address=host,
            port=int(port),
            user=username,
            password=password,
            encrypt=encrypt,
            sslValidateCertificate=verify_ssl
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION FROM SYS.M_DATABASE")
        version = cursor.fetchone()[0]
        
        cursor.execute("SELECT DATABASE_NAME, HOST FROM SYS.M_DATABASE")
        row = cursor.fetchone()
        db_name = row[0]
        db_host = row[1]
        
        # Get schema count
        cursor.execute("SELECT COUNT(*) FROM SYS.SCHEMAS WHERE HAS_PRIVILEGES = 'TRUE'")
        schema_count = cursor.fetchone()[0]
        
        conn.close()
        return True, f"Successfully authenticated to SAP HANA {version}\nDatabase: {db_name}\nHost: {db_host}\nAccessible Schemas: {schema_count}"
        
    except Exception as e:
        return False, f"SAP HANA error: {e}"

