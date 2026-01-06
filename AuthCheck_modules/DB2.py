# IBM DB2 Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "IBM DB2 (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "50000",
     "port_toggle": "use_ssl", "tls_port": "50001", "non_tls_port": "50000"},
    {"name": "database", "type": "text", "label": "Database Name"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "use_ssl", "type": "checkbox", "label": "Enable SSL"},
    {"name": "ssl_client_keydb", "type": "file", "label": "SSL Key Database", "filter": "Key Database (*.kdb);;All Files (*)"},
    {"name": "ssl_client_stash", "type": "file", "label": "SSL Stash File", "filter": "Stash Files (*.sth);;All Files (*)"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "TLS: 50001, Non-TLS: 50000. db2inst1 / db2inst1, db2admin / db2admin"},
]


def authenticate(form_data):
    """
    Attempt to authenticate to IBM DB2.
    
    Args:
        form_data (dict): Form field values
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        import ibm_db
    except ImportError:
        return False, "ibm_db package not installed. Run: pip install ibm_db"
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '').strip()
    database = form_data.get('database', '').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    use_ssl = form_data.get('use_ssl', False)
    ssl_client_keydb = form_data.get('ssl_client_keydb', '').strip()
    ssl_client_stash = form_data.get('ssl_client_stash', '').strip()
    
    if not host:
        return False, "Host is required"
    if not port:
        return False, "Port is required"
    if not database:
        return False, "Database name is required"
    if not username:
        return False, "Username is required"
    
    try:
        # Build connection string
        conn_str = f"DATABASE={database};HOSTNAME={host};PORT={port};PROTOCOL=TCPIP;UID={username};PWD={password};"
        
        if use_ssl:
            conn_str += "SECURITY=SSL;"
            if ssl_client_keydb:
                conn_str += f"SSLClientKeystoredb={ssl_client_keydb};"
            if ssl_client_stash:
                conn_str += f"SSLClientKeystash={ssl_client_stash};"
        
        # Attempt connection
        conn = ibm_db.connect(conn_str, "", "")
        
        if conn:
            # Get server info
            server_info = ibm_db.server_info(conn)
            db_name = server_info.DBNAME if hasattr(server_info, 'DBNAME') else database
            db_version = server_info.DBMS_VER if hasattr(server_info, 'DBMS_VER') else 'unknown'
            
            ibm_db.close(conn)
            
            return True, f"Successfully authenticated to DB2\nDatabase: {db_name}\nVersion: {db_version}"
        else:
            return False, "Connection returned None"
            
    except Exception as e:
        error_msg = str(e)
        # Parse common DB2 error codes
        if "SQL30082N" in error_msg:
            return False, "DB2 SQL30082N: Security processing failed - invalid credentials"
        elif "SQL1403N" in error_msg:
            return False, "DB2 SQL1403N: Database not found"
        elif "SQL30081N" in error_msg:
            return False, "DB2 SQL30081N: Communication error - check host/port"
        else:
            return False, f"DB2 error: {e}"

