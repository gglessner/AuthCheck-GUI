# Azure SQL Database Authentication Module
# Copyright (C) 2025 Garland Glessner - gglessner@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

module_description = "Azure SQL Database (Cloud)"

form_fields = [
    {"name": "server", "type": "text", "label": "Server Name"},
    {"name": "database", "type": "text", "label": "Database", "default": "master"},
    {"name": "username", "type": "text", "label": "Username"},
    {"name": "password", "type": "password", "label": "Password"},
    {"name": "auth_type", "type": "combo", "label": "Authentication", "options": ["SQL Authentication", "Azure AD Password", "Azure AD Integrated"], "default": "SQL Authentication"},
    {"name": "hints", "type": "readonly", "label": "Hints", "default": "Server: servername.database.windows.net. Admin user set during creation."},
]


def authenticate(form_data):
    """Attempt to authenticate to Azure SQL Database."""
    try:
        import pyodbc
    except ImportError:
        return False, "pyodbc package not installed. Run: pip install pyodbc"
    
    server = form_data.get('server', '').strip()
    database = form_data.get('database', 'master').strip()
    username = form_data.get('username', '').strip()
    password = form_data.get('password', '')
    auth_type = form_data.get('auth_type', 'SQL Authentication')
    
    if not server:
        return False, "Server Name is required"
    
    # Add Azure suffix if not present
    if not server.endswith('.database.windows.net'):
        server = f"{server}.database.windows.net"
    
    try:
        if auth_type == "SQL Authentication":
            if not username:
                return False, "Username is required"
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30"
        elif auth_type == "Azure AD Password":
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};Authentication=ActiveDirectoryPassword;Encrypt=yes"
        else:  # Azure AD Integrated
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Authentication=ActiveDirectoryIntegrated;Encrypt=yes"
        
        conn = pyodbc.connect(conn_str, timeout=30)
        cursor = conn.cursor()
        
        # Get version and edition
        cursor.execute("SELECT @@VERSION, SERVERPROPERTY('Edition')")
        row = cursor.fetchone()
        version = row[0].split('\n')[0] if row[0] else 'unknown'
        edition = row[1] if row[1] else 'unknown'
        
        # Get database count
        cursor.execute("SELECT COUNT(*) FROM sys.databases")
        db_count = cursor.fetchone()[0]
        
        conn.close()
        return True, f"Successfully authenticated to Azure SQL\n{edition}\nVersion: {version[:50]}...\nDatabases: {db_count}"
        
    except Exception as e:
        return False, f"Azure SQL error: {e}"

