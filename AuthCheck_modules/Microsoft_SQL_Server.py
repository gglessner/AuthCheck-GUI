# Microsoft SQL Server Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Microsoft SQL Server (DB)"

form_fields = [
    {"name": "host", "type": "text", "label": "Server Host", "default": "localhost"},
    {"name": "port", "type": "text", "label": "Port", "default": "1433",
     "port_toggle": "encrypt", "tls_port": "1433", "non_tls_port": "1433"},
    {"name": "database", "type": "text", "label": "Database", "default": "master"},
    {"name": "username", "type": "text", "label": "Username", "default": "sa"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "auth_type", "type": "combo", "label": "Authentication", "options": ["SQL Server", "Windows (NTLM)", "Windows (Kerberos)"], "default": "SQL Server"},
    {"name": "encrypt", "type": "checkbox", "label": "Encrypt Connection"},
    {"name": "trust_cert", "type": "checkbox", "label": "Trust Server Certificate"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Port 1433 (TLS/non-TLS same). sa / (set during install). Windows Auth."},
]


def authenticate(form_data):
    """Attempt to authenticate to Microsoft SQL Server."""
    try:
        import pymssql
    except ImportError:
        try:
            import pyodbc
            use_pyodbc = True
        except ImportError:
            return False, "pymssql or pyodbc package not installed. Run: pip install pymssql"
        use_pyodbc = True
    else:
        use_pyodbc = False
    
    host = form_data.get('host', '').strip()
    port = form_data.get('port', '1433').strip()
    database = form_data.get('database', 'master').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    auth_type = form_data.get('auth_type', 'SQL Server')
    encrypt = form_data.get('encrypt', False)
    trust_cert = form_data.get('trust_cert', False)
    
    if not host:
        return False, "Server Host is required"
    
    try:
        if use_pyodbc:
            import pyodbc
            if auth_type == "SQL Server":
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host},{port};DATABASE={database};UID={username};PWD={password}"
            else:
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={host},{port};DATABASE={database};Trusted_Connection=yes"
            
            if encrypt:
                conn_str += ";Encrypt=yes"
            if trust_cert:
                conn_str += ";TrustServerCertificate=yes"
            
            conn = pyodbc.connect(conn_str, timeout=10)
        else:
            conn = pymssql.connect(
                server=host,
                port=int(port),
                user=username,
                password=password,
                database=database,
                timeout=10
            )
        
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION, @@SERVERNAME, DB_NAME()")
        row = cursor.fetchone()
        
        version = row[0].split('\n')[0] if row[0] else 'unknown'
        server_name = row[1] if row[1] else 'unknown'
        current_db = row[2] if row[2] else database
        
        # Get database count
        cursor.execute("SELECT COUNT(*) FROM sys.databases")
        db_count = cursor.fetchone()[0]
        
        conn.close()
        return True, f"Successfully authenticated to SQL Server\nServer: {server_name}\nVersion: {version}\nDatabase: {current_db}\nTotal Databases: {db_count}"
        
    except Exception as e:
        return False, f"SQL Server error: {e}"

